
import pandas as pd
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import relation, relationship
from HardwareSwap.Models.database import Base
from HardwareSwap.Models.tools import get_or_create

class Brand(Base):
    __tablename__ = "brand"

    id = Column(Integer, primary_key=True)
    brand = Column(String)
