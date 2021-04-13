from datetime import datetime
from typing import Collection
from sqlalchemy import Column, Integer,JSON,DateTime

from .database import Base


class Log(Base):
    __tablename__ = "log"
    id = Column(Integer, primary_key=True, index=True)
    data = Column(JSON)
    date = Column(DateTime , default=datetime.today())
    