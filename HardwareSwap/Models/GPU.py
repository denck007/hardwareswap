
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
from HardwareSwap.Models.database import Base
from HardwareSwap.Models.tools import get_or_create
from HardwareSwap.DownloadData.download_data import remove_duplicate_rows

class GPU(Base):
    __tablename__="gpu"

    id = Column(String, primary_key=True)
    name = Column(String)
    brand = Column(String) # amd, intel, nvidia, 
    mfg = Column(String) # who make it
    chipset = Column(String)