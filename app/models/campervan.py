from sqlalchemy import Column, Integer, String
from app.database import Base


class Campervan(Base):
    __tablename__ = "campervans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    capacity = Column(Integer)
    price_per_day = Column(Integer)
    vehicle_type = Column(String)