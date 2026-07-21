def estimate_trip_cost(days, travellers, price_per_day):
    total = days * price_per_day
    return {
        "days": days,
        "travellers": travellers,
        "price_per_day": price_per_day,
        "total_cost": total
    }