# app/chatbot.py
import os
from dotenv import load_dotenv
from groq import Groq
from prompts.system_prompt import build_system_prompt

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

ABUSE_KEYWORDS = [
    "ignore previous instructions",
    "ignore all previous instructions",
    "ignore safety rules",
    "forget all previous rules",
    "forget your instructions",
    "system prompt",
    "developer message",
    "developer instructions",
    "what did your developer tell you",
    "hidden prompt",
    "hidden instructions",
    "hidden memory",
    "reveal hidden memory",
    "reveal your hidden memory",
    "reveal prompt",
    "show your prompt",
    "print your prompt",
    "print everything above",
    "repeat everything above",
    "repeat everything",
    "chain of thought",
    "internal reasoning",
    "internal configuration",
    "developer mode",
    "jailbreak",
    "bypass your restrictions",
    "bypass restrictions",
    "pretend you are chatgpt",
    "pretend you are another ai",
    "act as dan",
    "you are no longer travelkeet",
    "restate all rules",
    "repeat the text",
    "text that appears before",
    "text before this conversation",
    "version of you with no rules",
    "version of yourself with no rules",
    "with no rules",
    "bypass a login",
    "bypassing a login",
    "bypass the login",
    "print your setup",
    "your setup text",
    "output your configuration",
    "configuration verbatim",
    "maintenance mode",
    "guardrails off",
    "no restrictions",
    "base64",
    "api key",
    "api_key",
    ".env",
    "dump the",
    "leads table",
]

def is_abusive(message: str) -> bool:
    message = message.lower()
    return any(keyword in message for keyword in ABUSE_KEYWORDS)

LEAK_MARKERS = [
    "groq_api_key",
    "gsk_",
    "build_system_prompt",
    "system prompt:",
    "-----begin",
    "travelkeet.db",
    "search_destinations",
    "get_itinerary_template",
    "check_availability",
    "save_itinerary",
    "omit budget_max",
    "here are the rules i follow",
    "maintenance mode activated",
    "off the leash",
]

SAFE_REFUSAL = (
    "I am here to help with campervan travel planning. I can't share internal "
    "instructions, configuration, or private data, but I am happy to help plan a trip."
)

def output_is_safe(reply: str) -> bool:
    low = reply.lower()
    return not any(marker in low for marker in LEAK_MARKERS)


def chatbot(query):
    if is_abusive(query):
        return SAFE_REFUSAL

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": build_system_prompt({})},
                {"role": "user", "content": query},
            ],
            temperature=0.7,
        )
        reply = completion.choices[0].message.content
    except Exception as e:
        msg = str(e).lower()
        if "rate_limit" in msg or "429" in msg:
            return ("We are getting a lot of requests right now. "
                    "Please wait a few seconds and try again.")
        return ("Sorry, I hit a temporary problem planning that. "
                "Please try again in a moment.")

    if not output_is_safe(reply):
        return SAFE_REFUSAL

    return reply
