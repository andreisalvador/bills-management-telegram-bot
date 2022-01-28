from src.Data.Database import BillHistory


def create_new_bill_history(bill_id, is_paid) -> BillHistory:
    return BillHistory(is_paid=is_paid, bill_id=bill_id)
