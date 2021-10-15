
from sqlalchemy import Column, Integer, String
from HardwareSwap.Models.database import Base

class PostType(Base):
    __tablename__="post_type"

    id = Column(Integer, primary_key=True)
    post_type = Column(String, nullable=False)
