from sqlalchemy import create_engine, Column, Integer, String, Enum, Numeric, SmallInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.Enums.PeriodEnum import PeriodEnum

engine = create_engine('postgresql://postgres:123456@localhost:5432/test', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class Bill(Base):
    __tablename__ = 'Bills'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    value = Column(Numeric)
    expiration_day = Column(SmallInteger)
    expiration_period = Column(Enum(PeriodEnum))
    user_id = Column(String)


Base.metadata.create_all(engine)
