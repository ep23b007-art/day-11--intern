import re
import json
from groq import Groq
from app.core import config
from app.agent import tools as agent_tools
from prompts.system_prompt import build_system_prompt


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
                    "budget_max": {"type": "number"},
                },
                "required": ["query"],
            },
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
    "get_itinerary_template": agent_tools.get_itinerary_template,
    "check_availability": agent_tools.check_availability,
    "save_itinerary": agent_tools.save_itinerary,
}


def _extract_slots(history: list[dict]) -> dict:
    slots = {}
    text = " ".join(m["content"] for m in history if m["role"] == "user").lower()

    for city in ["bali", "tokyo", "paris", "london"]:
        if city in text:
            slots["destination"] = city.title()
            break

    m = re.search(r"(\d+)\s*day", text)
    if m:
        slots["duration_days"] = int(m.group(1))

    m = re.search(r"\$\s*([\d,]+)", text)
    if m:
        slots["budget"] = int(m.group(1).replace(",", ""))

    return slots


class AgentOrchestrator:
    def __init__(self):
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model_name = "llama-3.1-8b-instant"

    async def handle_message(
        self,
        session_id: str,
        user_message: str,
        history: list[dict]
    ) -> dict:

        full_history = history + [{"role": "user", "content": user_message}]
        slots = _extract_slots(full_history)
        system_prompt = build_system_prompt(slots)

        messages = [{"role": "system", "content": system_prompt + "\n\nIMPORTANT: When calling functions, you MUST use proper JSON format for arguments. Do not add any extra characters or text around the JSON."}]
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_message})

        tool_calls = []
        final_text = ""

        for iteration in range(5):
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=TOOL_DECLARATIONS,
                tool_choice="auto"
            )

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
                args = json.loads(tc.function.arguments)

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
            final_text = "I'm still working through the details — could you try again?"

        return {
            "reply": final_text,
            "tool_calls": tool_calls,
            "slots": slots
        }