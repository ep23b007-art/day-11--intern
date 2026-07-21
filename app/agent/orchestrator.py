import re
import json
from groq import Groq
from app.core import config
from app.agent import tools as agent_tools
from prompts.system_prompt import build_system_prompt
from app.agent.memory import get_window


TOOL_DECLARATIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_destinations",
            "description": "Search the database for travel destinations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "budget_max": {
                        "type": "number",
                        "description": (
                            "Optional. Omit this field entirely if the user "
                            "gave no budget. Never send null."
                        ),
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "estimate_trip_cost",
            "description": "Calculate the total trip cost.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string"
                    },
                    "days": {
                        "type": "integer"
                    }
                },
                "required": [
                    "destination",
                    "days"
                ]
            }
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_itinerary_template",
            "description": "Get a day-by-day itinerary template for a destination.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination_id": {"type": "string"},
                    "duration_days": {"type": "integer"},
                },
                "required": ["destination_id", "duration_days"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check hotel/flight availability.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination_id": {"type": "string"},
                    "check_in": {"type": "string"},
                    "check_out": {"type": "string"},
                    "num_travelers": {"type": "integer"},
                },
                "required": ["destination_id", "check_in", "check_out"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_itinerary",
            "description": "Save the finalised itinerary to the database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "itinerary": {"type": "object"},
                },
                "required": ["session_id", "itinerary"],
            },
        },
    },
]


TOOL_REGISTRY = {
    "search_destinations": agent_tools.search_destinations,
    "estimate_trip_cost": agent_tools.estimate_trip_cost,
    "get_itinerary_template": agent_tools.get_itinerary_template,
    "check_availability": agent_tools.check_availability,
    "save_itinerary": agent_tools.save_itinerary,
}

# Model text must never contain raw function-call syntax. This regex
# removes any leaked lines like:  /function=search_destinations>{...}
# or  <function=...>{...}</function>
_FUNCTION_LEAK = re.compile(r"^\s*<?/?function=.*$", re.MULTILINE)


def _clean_reply(text: str) -> str:
    """Strip leaked tool-call syntax from a model reply."""
    return _FUNCTION_LEAK.sub("", text or "").strip()


def _extract_slots(history: list[dict]) -> dict:
    slots = {}
    text = " ".join(m["content"] for m in history if m["role"] == "user").lower()

    cities = [
        "bali", "tokyo", "paris", "london",
        "chennai", "goa", "bangalore", "bengaluru", "mumbai", "delhi",
        "hyderabad", "pune", "manali", "leh", "coorg", "rishikesh",
        "pondicherry", "kochi", "munnar", "jaipur", "udaipur", "srisailam",
    ]
    for city in cities:
        if city in text:
            slots["destination"] = city.title()
            break

    m = re.search(r"(\d+)\s*day", text)
    if m:
        slots["duration_days"] = int(m.group(1))

    m = re.search(r"(?:\$|₹|rs\.?\s*|budget\s*)([\d,]+)", text)
    if m:
        slots["budget"] = int(m.group(1).replace(",", ""))

    m = re.search(r"(\d+)\s*(?:people|persons?|travellers?|travelers?|log|pax|kids?|adults?)", text)
    if m:
        slots["num_travelers"] = int(m.group(1))

    return slots


class AgentOrchestrator:
    def __init__(self):
        self.client = Groq(api_key=config.GROQ_API_KEY)
        # was "llama-3.1-8b-instant" — the 8B model kept leaking function
        # syntax into replies. 70B follows tool + format rules far better.
        self.model_name = "llama-3.3-70b-versatile"

    def _create(self, messages, use_tools=True):
        """One Groq call. use_tools=False forces a plain-text answer."""
        kwargs = {"model": self.model_name, "messages": messages}
        if use_tools:
            kwargs["tools"] = TOOL_DECLARATIONS
            kwargs["tool_choice"] = "auto"
        return self.client.chat.completions.create(**kwargs)

    async def handle_message(
        self,
        session_id: str,
        user_message: str,
        history: list[dict]
    ) -> dict:

        full_history = history + [{"role": "user", "content": user_message}]
        slots = _extract_slots(full_history)
        system_prompt = build_system_prompt(slots)

        messages = [{"role": "system", "content": system_prompt}]
        for msg in get_window(session_id, history):
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_message})

        tool_calls = []
        final_text = ""

        for iteration in range(5):
            # A bad generated tool call can make Groq itself return 400
            # ("tool call validation failed"). Instead of crashing the
            # whole request, fall back to a forced plain-text answer.
            try:
                response = self._create(messages, use_tools=True)
            except Exception:
                response = self._create(messages, use_tools=False)

            message = response.choices[0].message

            if not message.tool_calls:
                final_text = message.content or ""
                break

            messages.append({
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            })

            for tc in message.tool_calls:
                name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    args = {}
                # drop null params (e.g. budget_max: null) so our own
                # tool functions never receive None values
                args = {k: v for k, v in args.items() if v is not None}

                fn = TOOL_REGISTRY.get(name)
                try:
                    result = await fn(**args) if fn else {"error": "unknown tool"}
                except Exception as e:
                    result = {"error": str(e)}

                tool_calls.append({"name": name, "args": args, "result": result})

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result)
                })

        else:
            # loop hit 5 iterations while still calling tools: instead of
            # giving up with a canned apology, force one final answer
            # from everything gathered so far, with tools switched OFF.
            messages.append({
                "role": "user",
                "content": (
                    "Please write your final answer now using the "
                    "information gathered so far, following the required "
                    "7-section itinerary format."
                ),
            })
            try:
                response = self._create(messages, use_tools=False)
                final_text = response.choices[0].message.content or ""
            except Exception:
                final_text = ""

        final_text = _clean_reply(final_text)
        
        if not final_text:
            final_text = (
                "Sorry, I hit a snag putting that together. "
                "Could you rephrase your request?"
            ) 

        #Ask for name and phone only after itinerary generation
        if slots.get("destination") and slots.get("duration_days"):
            final_text += """
--------------------------------------------------

📞 Interested in this trip?

If you'd like our TravelKeet team to contact you regarding this itinerary, please reply with:

• Name:
• Indian Phone Number:

Example:
Name: Neha
Phone: 9876543210

We'll use these details only to help you with your booking and trip planning.
"""

        return {
            "reply": final_text,
            "tool_calls": tool_calls,
            "slots": slots
        }