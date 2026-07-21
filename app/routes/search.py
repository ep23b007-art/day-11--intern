from fastapi import APIRouter
from app.database import SessionLocal
from app.agent.search_campervans import search_campervans

router = APIRouter()


@router.get("/search")
def search(destination: str):

    db = SessionLocal()

    result = search_campervans(db, destination)

    db.close()

    return result