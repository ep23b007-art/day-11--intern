import re
from app.database import SessionLocal
from app.models.lead import Lead
from app.agent.trip_summary import generate_trip_summary


def is_valid_phone(phone: str):
    pattern = r"^(?:\+91|91)?[6-9]\d{9}$"
    return bool(re.fullmatch(pattern, phone))


def save_lead(
    name,
    phone,
    destination,
    days,
    travellers,
    recommended_van,
    trip_summary,
):

    if not is_valid_phone(phone):
        return {
            "success": False,
            "message": "Invalid Indian phone number."
        }

    db = SessionLocal()

    trip_summary = generate_trip_summary(
    destination,
    days,
    travellers,
    recommended_van,
)

    lead = Lead(
        name=name,
        phone=phone,
        destination=destination,
        days=days,
        travellers=travellers,
        recommended_van=recommended_van,
        trip_summary=trip_summary,
    )

    db.add(lead)
    db.commit()
    db.close()

    return {
        "success": True,
        "message": "Lead saved successfully."
    }