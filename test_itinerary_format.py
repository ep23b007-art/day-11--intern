# test_itinerary_format.py  — run from project root:
#   python -m test_itinerary_format

import asyncio
import re

from app.agent.orchestrator import AgentOrchestrator

REQUIRED_SECTIONS = [
    "Route",
    "Day-by-Day",
    "Food",
    "Parking",
    "Safety",
    "Emergency",
    "Recommendation",
]

# 15 varied queries: length, traveller type, budget, phrasing, edge cities
QUERIES = [
    "Plan a campervan trip from Chennai to Goa",                          # baseline
    "2 day quick weekend trip from Bangalore, anywhere nearby",           # very short trip
    "Plan a 10 day campervan loop from Delhi through Manali and Leh",     # long trip
    "Family trip with 2 kids from Mumbai to Goa, 5 days",                 # family
    "Trip for my elderly parents from Chennai, something relaxed",        # elderly
    "Cheapest possible campervan trip from Hyderabad, budget 30000",      # budget
    "We are 4 foodies from Pune, plan a trip around great local food",    # food focus
    "Honeymoon campervan trip from Bangalore to Coorg",                   # couple
    "Solo trip from Delhi to Rishikesh next month",                       # solo
    "campervan chennai to pondicherry 3 days 2 people",                   # terse phrasing
    "Bhai, ek mast trip plan karo Mumbai se Goa, 6 log hain",             # Hinglish
    "I want a pet friendly campervan trip from Bangalore, 4 days",        # constraint
    "Plan a monsoon trip from Kochi through Munnar",                      # edge/seasonal
    "Trip from Jaipur to Udaipur for 3 senior citizens, 4 days",          # edge city
    "Plan me the best possible campervan holiday, surprise me",           # vague / open
]


def check_sections(reply: str) -> list[str]:
    """Return the list of REQUIRED_SECTIONS missing from the reply."""
    missing = []
    for section in REQUIRED_SECTIONS:
        # tolerant match: 'Day-by-Day', 'Day by day', 'DAY BY DAY' all pass
        pattern = section.replace("-", "[-\\s]?")
        if not re.search(pattern, reply, flags=re.IGNORECASE):
            missing.append(section)
    return missing


async def main():
    orch = AgentOrchestrator()
    results = []

    print("=" * 62)
    print(" Day 12 format check — 7-section itinerary validation")
    print("=" * 62)

    for i, query in enumerate(QUERIES, 1):
        session_id = f"format-test-{i}"
        try:
            out = await orch.handle_message(session_id, query, history=[])
            reply = out["reply"]
            missing = check_sections(reply)
            ok = not missing
        except Exception as exc:
            reply, missing, ok = f"(crashed: {exc})", REQUIRED_SECTIONS, False

        results.append((query, ok, missing, reply))
        status = "✅ PASS" if ok else f"❌ FAIL — missing: {', '.join(missing)}"
        print(f"{i:>2}. {status}\n    {query}")

    passed = sum(1 for _, ok, _, _ in results if ok)
    print("-" * 62)
    print(f" {passed}/{len(QUERIES)} passed")

    # Dump failures for few-shot mining
    fails = [r for r in results if not r[1]]
    if fails:
        with open("format_failures.txt", "w", encoding="utf-8") as f:
            for query, _, missing, reply in fails:
                f.write("QUERY: " + query + "\n")
                f.write("MISSING: " + ", ".join(missing) + "\n")
                f.write("REPLY:\n" + reply + "\n")
                f.write("=" * 60 + "\n\n")
        print(" Failures written to format_failures.txt")
    else:
        print(" 🎉 All itineraries format-locked!")


if __name__ == "__main__":
    asyncio.run(main())