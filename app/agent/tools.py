async def search_destinations(query: str, budget_max: float = None):
    # stub for now if DB isn't ready
    return [{"id": "dest_1", "name": "Bali", "country": "Indonesia"}]


async def get_itinerary_template(destination_id: str, duration_days: int):
    return {"days": [{"day": 1, "activities": ["Arrival", "Beach walk"]}]}


async def check_availability(destination_id: str, check_in: str, check_out: str, num_travelers: int = 1):
    return {"available": True, "price_per_night": 120}


async def save_itinerary(session_id: str, itinerary: dict):
    return {"saved": True}