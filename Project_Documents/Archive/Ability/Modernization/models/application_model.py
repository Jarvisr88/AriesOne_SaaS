from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

class ApplicationSQL(Base):
    __tablename__ = 'applications'
    id = Column(Integer, primary_key=True, index=True)
    facility_state = Column(String)
    line_of_business = Column(String)
    name = Column(String)
    data_center = Column(String)
    app_id = Column(String)
    pptn_region = Column(String)

class Application(BaseModel):
    facility_state: str
    line_of_business: str
    name: str
    data_center: str
    app_id: str
    pptn_region: str

    class Config:
        orm_mode = True
