import datetime

from sqlalchemy import create_engine, Column, Integer, String, Enum, Numeric, SmallInteger, Boolean, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

from src.Enums.PeriodEnum import PeriodEnum

engine = create_engine(os.environ['CONNECTION_STRING'], echo=True)
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
    user_id = Column(Integer)
    created_at = Column(Date, default=datetime.datetime.now())

class BillHistory(Base):
    __tablename__ = 'BillsHistory'

    id = Column(Integer, primary_key=True)
    expiration_date = Column(Date, nullable=False)
    payment_date = Column(Date, nullable=True)
    is_paid = Column(Boolean, default=False)
    is_value_changed = Column(Boolean, default=False)
    value_payed = Column(Numeric, default=0)
    bill_id = Column(Integer, ForeignKey('Bills.id'))


Base.metadata.create_all(engine)
