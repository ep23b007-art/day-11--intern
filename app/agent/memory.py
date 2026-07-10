from groq import Groq
from app.core import config

MAX_TURNS = 15
SUMMARY_MODEL = "llama-3.1-8b-instant"

_client = Groq(api_key=config.GROQ_API_KEY)


def summarize_history(older_messages: list[dict]) -> str:
    """
    Summarize conversation history older than the sliding window.
    """

    if not older_messages:
        return ""

    transcript = "\n".join(
        f"{msg['role']}: {msg['content']}"
        for msg in older_messages
    )

    try:
        response = _client.chat.completions.create(
            model=SUMMARY_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Summarize this travel planning conversation in under "
                        "100 words. Keep only important planning facts such as "
                        "origin, destination, travel dates, travellers, budget, "
                        "preferences and decisions. Ignore greetings."
                    ),
                },
                {
                    "role": "user",
                    "content": transcript,
                },
            ],
            max_tokens=200,
        )

        return response.choices[0].message.content or ""

    except Exception:
        return ""


def get_window(
    conv_id: str,
    history: list[dict],
    max_turns: int = MAX_TURNS,
) -> list[dict]:
    """
    Returns conversation window to send to Groq.
    """

    max_messages = max_turns * 2

    if len(history) <= max_messages:
        return history

    older = history[:-max_messages]
    recent = history[-max_messages:]

    summary = summarize_history(older)

    if not summary:
        return recent

    summary_message = {
        "role": "system",
        "content": (
            "Summary of earlier conversation: "
            f"{summary}"
        ),
    }

    return [summary_message] + recent