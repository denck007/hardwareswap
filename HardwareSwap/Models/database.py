from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

db_uri = 'sqlite:///hardwareswap.db'
engine = create_engine(db_uri, echo = False)
Base = declarative_base()
