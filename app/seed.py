from app.database import SessionLocal
from app.models.campervan import Campervan

db = SessionLocal()

if db.query(Campervan).count() == 0:

    vans = [

        Campervan(
            name="Goa Beach Explorer",
            destination="Goa",
            capacity=4,
            price_per_day=5000,
            vehicle_type="Luxury"
        ),

        Campervan(
            name="Manali Adventure",
            destination="Manali",
            capacity=5,
            price_per_day=6500,
            vehicle_type="SUV"
        ),

        Campervan(
            name="Kerala Nature Ride",
            destination="Kerala",
            capacity=4,
            price_per_day=4500,
            vehicle_type="Standard"
        )

    ]

    db.add_all(vans)
    db.commit()

print("Database Seeded Successfully!")