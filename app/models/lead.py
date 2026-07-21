from sqlalchemy import Column, Integer, String
from app.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)
    phone = Column(String)

    destination = Column(String)
    days = Column(Integer)
    travellers = Column(Integer)

    recommended_van = Column(String)
    trip_summary = Column(String)