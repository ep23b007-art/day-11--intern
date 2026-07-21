from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.models.campervan import Campervan
from app.models.lead import Lead

from app.routes.search import router as search_router
from app.routes.lead import router as lead_router


app = FastAPI(
    title="TravelKeet AI Planner",
    version="1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",          # Local testing
        "http://127.0.0.1:5500",
        "https://travelkeet.com",         # Production
        "https://staging.travelkeet.com"  # Staging
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router)
app.include_router(lead_router)

Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {
        "message": "Welcome to TravelKeet AI Planner!"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }