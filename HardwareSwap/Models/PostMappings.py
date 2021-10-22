
import pandas as pd
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import relation, relationship
from HardwareSwap.Models.database import Base
from HardwareSwap.Models.tools import get_or_create


class PostBrand(Base):
    __tablename__ = "post_brand"

    id = Column(Integer, primary_key=True)
    brand_id = Column(Integer, ForeignKey("brand.id"))
    post_id = Column(String, ForeignKey("post.id"))


class PostManufacturer(Base):
    __tablename__ = "post_manufacturer"

    id = Column(Integer, primary_key=True)
    manufacturer_id = Column(Integer, ForeignKey("manufacturer.id"))
    post_id = Column(String, ForeignKey("post.id"))


class PostSeries(Base):
    __tablename__ = "post_series"

    id = Column(Integer, primary_key=True)
    series_id = Column(Integer, ForeignKey("series.id"))
    post_id = Column(String, ForeignKey("post.id"))
