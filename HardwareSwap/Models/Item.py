
from sqlalchemy.sql.schema import ForeignKey, Index
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import relation, relationship
from HardwareSwap.Models.database import Base
from HardwareSwap.Models.tools import get_or_create

class Item(Base):
    __tablename__ = "item"
    __table_args__ = (Index('ix_Item_postid_postdate_number_variant_edition_price', "post_id", "number", "variant", "edition", "price", "post_date"), )

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("post.id"), nullable=False)
    post_date = Column(DateTime)

    item_type_id = Column(Integer, ForeignKey("item_type.id"), index=True, nullable=False)
    item_type = relationship("ItemType", back_populates="items")

    brand_id = Column(Integer, ForeignKey("brand.id"), index=True, nullable=True)
    manufacturer_id = Column(Integer, ForeignKey("manufacturer.id"), index=True, nullable=True)
    manufacturer_model = Column(String, nullable=True)

    number = Column(String, index=True, nullable=False)
    variant = Column(String, index=True, nullable=True)
    edition = Column(String, index=True, nullable=True)

    price = Column(Float, index=True)
    price_possibly_external = Column(Boolean, default=False)

    # The index ranges in the post used to generate this entry
    location_in_post_start = Column(Integer, nullable=False)
    location_in_post_end = Column(Integer, nullable=False)


class ItemType(Base):
    __tablename__ = "item_type"
    id = Column(Integer, primary_key=True)
    item_type = Column(String, nullable=False)
    items = relationship("Item", back_populates="item_type")
