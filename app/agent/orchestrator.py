import re
from google import genai
from google.genai import types
from app.agent import tools as agent_tools
from app.integrations.gemini import get_gemini_model
from prompts.system_prompt import build_system_prompt


TOOL_DECLARATIONS = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="search_destinations",
            description="Search the database for travel destinations.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "query": types.Schema(type="STRING"),
                    "budget_max": types.Schema(type="NUMBER"),
                },
                required=["query"],
            ),
        ),
        types.FunctionDeclaration(
            name="get_itinerary_template",
            description="Get a day-by-day itinerary template for a destination.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "destination_id": types.Schema(type="STRING"),
                    "duration_days": types.Schema(type="INTEGER"),
                },
                required=["destination_id", "duration_days"],
            ),
        ),
        types.FunctionDeclaration(
            name="check_availability",
            description="Check hotel/flight availability.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "destination_id": types.Schema(type="STRING"),
                    "check_in": types.Schema(type="STRING"),
                    "check_out": types.Schema(type="STRING"),
                    "num_travelers": types.Schema(type="INTEGER"),
                },
                required=["destination_id", "check_in", "check_out"],
            ),
        ),
        types.FunctionDeclaration(
            name="save_itinerary",
            description="Save the finalised itinerary to the database.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "session_id": types.Schema(type="STRING"),
                    "itinerary": types.Schema(type="OBJECT"),
                },
                required=["session_id", "itinerary"],
            ),
        ),
    ]
)


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


def _to_gemini_history(history: list[dict]) -> list:
    gemini_msgs = []
    for msg in history:
        role = "model" if msg["role"] == "assistant" else "user"
        gemini_msgs.append({"role": role, "parts": [{"text": msg["content"]}]})
    return gemini_msgs


class AgentOrchestrator:
    def __init__(self):
        self.client = get_gemini_model()
        self.model_name = "gemini-2.0-flash"

    async def handle_message(
        self,
        session_id: str,
        user_message: str,
        history: list[dict]
    ) -> dict:

        full_history = history + [{"role": "user", "content": user_message}]
        slots = _extract_slots(full_history)
        system_prompt = build_system_prompt(slots)
        gemini_history = _to_gemini_history(history)

        current_message = system_prompt + "\n\nUser: " + user_message
        tool_calls = []
        final_text = ""

        messages = gemini_history + [{"role": "user", "parts": [{"text": current_message}]}]

        for iteration in range(5):
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=messages,
                config=types.GenerateContentConfig(tools=[TOOL_DECLARATIONS])
            )

            candidate = response.candidates[0]
            parts = candidate.content.parts

            function_calls = [p for p in parts if hasattr(p, "function_call") and p.function_call]

            if not function_calls:
                final_text = "\n".join(
                    p.text for p in parts if hasattr(p, "text") and p.text
                )
                break

            function_responses = []
            for fc in function_calls:
                name = fc.function_call.name
                args = dict(fc.function_call.args)

                fn = TOOL_REGISTRY.get(name)
                try:
                    result = await fn(**args) if fn else {"error": "unknown tool"}
                except Exception as e:
                    result = {"error": str(e)}

                tool_calls.append({"name": name, "args": args, "result": result})
                function_responses.append({
                    "role": "tool",
                    "parts": [{"function_response": {"name": name, "response": result}}]
                })

            messages = messages + function_responses

        else:
            final_text = "I'm still working through the details — could you try again?"

        # DB persist commented out until app.db is ready
        # async with get_db_session() as db:
        #     await crud.append_message(db, session_id=session_id, role="user", content=user_message)
        #     await crud.append_message(db, session_id=session_id, role="assistant", content=final_text, tool_calls=tool_calls)
        #     await db.commit()

        return {
            "reply": final_text,
            "tool_calls": tool_calls,
            "slots": slots
        }