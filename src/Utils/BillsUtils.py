import datetime
from dateutil.relativedelta import relativedelta

from src.Data.Database import BillHistory, Bill


def create_new_bill_history(bill: Bill) -> BillHistory:
    today = datetime.datetime.now()
    day = int(bill.expiration_day)

    if day <= today.day:
        return create_new_bill_history_adding_months(bill.id, day, bill.expiration_period.value)
    else:
        return create_new_bill_history_adding_months(bill.id, day, 0)


def create_new_bill_history_adding_months(bill_id, expiration_day, months_to_add) -> BillHistory:
    today = datetime.datetime.now()
    result_date = today + relativedelta(months=months_to_add, day=expiration_day)

    return BillHistory(expiration_date=result_date, is_paid=False, bill_id=bill_id)
