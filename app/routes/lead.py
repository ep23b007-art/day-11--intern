from fastapi import APIRouter

from app.agent.save_lead import save_lead
from app.agent.trip_summary import generate_trip_summary

router = APIRouter()


@router.post("/lead")
def create_lead(data: dict):

    summary = generate_trip_summary(
        data["destination"],
        data["days"],
        data["travellers"],
    )

    return save_lead(
        name=data["name"],
        phone=data["phone"],
        destination=data["destination"],
        days=data["days"],
        travellers=data["travellers"],
        recommended_van=data["recommended_van"],
        trip_summary=summary,
    )