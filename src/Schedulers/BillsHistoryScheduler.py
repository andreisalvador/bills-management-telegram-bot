import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import extract

from src.Data.Database import session, Bill, BillHistory
from src.Enums.PeriodEnum import PeriodEnum
from src.Utils.BillsUtils import create_new_bill_history_adding_months


class BillsHistoryScheduler:
    def __init__(self):
        self.__execution_day = 1
        self.__scheduler = BlockingScheduler()

    def create_bills_history_for_monthly_bills(self):
        today = datetime.datetime.now()

        if today.day == self.__execution_day:
            monthly_bills = session.query(Bill).join(BillHistory, Bill.id == BillHistory.bill_id).filter(
                Bill.expiration_period == PeriodEnum.Monthly, extract('day', Bill.created_at) < Bill.expiration_day,
                Bill.created_at <= today, BillHistory.is_paid == False).all()

            bills_histories = [create_new_bill_history_adding_months(bill.id, bill.expiration_day, 1) for
                               bill
                               in monthly_bills]

            for bill in bills_histories:
                print(f'{bill.expiration_date}')

            session.bulk_save_objects(bills_histories)
            session.commit()

    def start_jobs(self):
        self.__scheduler.add_job(self.create_bills_history_for_monthly_bills, 'cron', day=self.__execution_day)
        self.__scheduler.start()
