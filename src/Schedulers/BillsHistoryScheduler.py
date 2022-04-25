import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from dateutil.relativedelta import relativedelta
from sqlalchemy import extract
from sqlalchemy.orm import load_only, Load

from src.Data.Database import session, Bill, BillHistory
from src.Enums.PeriodEnum import PeriodEnum
from src.Utils.BillsUtils import create_new_bill_history_adding_months


def create_bills_history_for_monthly_bills():
    today = datetime.datetime.now()
    next_date = today + relativedelta(months=1)
    month = next_date.month
    year = next_date.year
    subquery = session.query(BillHistory.bill_id).options(load_only("bill_id")) \
        .filter(extract('month', BillHistory.expiration_date) == month,
                extract('year', BillHistory.expiration_date) == year)

    monthly_bills = session.query(Bill).join(BillHistory, Bill.id == BillHistory.bill_id) \
        .options(Load(Bill).load_only(Bill.id, Bill.expiration_day)) \
        .filter(Bill.expiration_period == PeriodEnum.Monthly, Bill.id.not_in(subquery)).all()

    bills_histories = [create_new_bill_history_adding_months(bill.id, bill.expiration_day, 1) for
                       bill
                       in monthly_bills]

    session.bulk_save_objects(bills_histories)
    session.commit()


class BillsHistoryScheduler:
    def __init__(self):
        self.__scheduler = BlockingScheduler()

    def start_jobs(self):
        self.__scheduler.add_job(create_bills_history_for_monthly_bills, trigger='cron', year='*', month='*',
                                 day='last')
        self.__scheduler.start()
