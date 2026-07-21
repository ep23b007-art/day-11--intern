def generate_trip_summary(destination, days, travellers, recommended_van):
    return (
        f"{days}-day trip to {destination} "
        f"for {travellers} travellers. "
        f"Recommended campervan: {recommended_van}."
    )