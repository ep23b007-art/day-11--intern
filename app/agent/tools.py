from difflib import get_close_matches

# Sample campervan inventory
CAMPERVANS = [
    {
        "id": "van1",
        "name": "Goa Explorer",
        "destination": "Goa",
        "price_per_day": 4500,
    },
    {
        "id": "van2",
        "name": "Coorg Adventure",
        "destination": "Coorg",
        "price_per_day": 5000,
    },
    {
        "id": "van3",
        "name": "Manali Mountain Rider",
        "destination": "Manali",
        "price_per_day": 6000,
    },
]


async def search_destinations(query: str, budget_max: float = None):

    matches = []

    for van in CAMPERVANS:
        if query.lower() in van["destination"].lower():

            if budget_max is None or van["price_per_day"] <= budget_max:
                matches.append(van)

    if matches:
        return matches

    # No exact match → show closest
    destinations = [van["destination"] for van in CAMPERVANS]

    closest = get_close_matches(query, destinations, n=1)

    if closest:

        for van in CAMPERVANS:

            if van["destination"] == closest[0]:

                return {
                    "message": "No exact match found. Showing closest available campervan.",
                    "closest_match": van,
                }

    return {
        "message": "No campervan available."
    }


async def estimate_trip_cost(destination: str, days: int):

    for van in CAMPERVANS:

        if van["destination"].lower() == destination.lower():

            return {
                "destination": destination,
                "days": days,
                "price": van["price_per_day"] * days,
            }

    return {
        "error": "Destination not found."
    }


async def get_itinerary_template(destination_id: str, duration_days: int):

    return {
        "days": [
            {
                "day": 1,
                "activities": [
                    "Arrival",
                    "Local Sightseeing",
                ],
            }
        ]
    }


async def check_availability(
    destination_id: str,
    check_in: str,
    check_out: str,
    num_travelers: int = 1,
):

    return {
        "available": True,
        "price_per_night": 120,
    }


async def save_itinerary(session_id: str, itinerary: dict):

    return {
        "saved": True
    }