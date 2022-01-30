import datetime
from dateutil.relativedelta import relativedelta

from src.Data.Database import BillHistory
from src.Enums.PeriodEnum import PeriodEnum


def create_new_bill_history(expiration_day, expiration_period: PeriodEnum, bill_id, is_paid) -> BillHistory:
    today = datetime.datetime.now()
    day = int(expiration_day)

    if day <= today.day:
        result_date = today + relativedelta(months=expiration_period.value)
    else:
        result_date = today + relativedelta(months=0)

    return BillHistory(expiration_date=datetime.datetime(result_date.year, result_date.month, day), is_paid=is_paid, bill_id=bill_id)
