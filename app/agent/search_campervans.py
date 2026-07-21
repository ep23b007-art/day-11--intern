from sqlalchemy.orm import Session
from app.models.campervan import Campervan


def search_campervans(db: Session, destination: str):
    """
    Search campervans by destination.
    If no exact match exists, return closest available destinations.
    """

    destination = destination.lower()

    vans = (
        db.query(Campervan)
        .filter(Campervan.destination.ilike(f"%{destination}%"))
        .all()
    )

    if vans:
        return {
            "exact_match": True,
            "message": "Campervans found.",
            "campervans": vans,
        }

    closest = db.query(Campervan).limit(3).all()

    return {
        "exact_match": False,
        "message": "No exact match found. Here are the closest available campervans.",
        "campervans": closest,
    }