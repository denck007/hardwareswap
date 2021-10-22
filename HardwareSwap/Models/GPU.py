
import datetime
import json
import pandas as pd
import pytz
import re
import tqdm
import sys
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import relation, relationship
from HardwareSwap.Models.Manufacturer import Manufacturer
from HardwareSwap.Models.database import Base
from HardwareSwap.Models.tools import get_or_create
from HardwareSwap.DownloadData.download_data import remove_duplicate_rows

class GPU(Base):
    __tablename__="gpu"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    brand_id = Column(Integer, ForeignKey("brand.id"))
    manufacturer_id = Column(Integer, ForeignKey("manufacturer.id"))
    series_id = Column(Integer, ForeignKey("series.id"))

    chipset = Column(String)
    prefix = Column(String)
    number = Column(Integer)

    pcpartpicker_url = Column(String)
    pcpartpicker_price = Column(Float)
