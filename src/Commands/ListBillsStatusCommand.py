import datetime

from sqlalchemy import extract
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from src.Data.Database import session, Bill, BillHistory

from src.Commands.Base.CommandBase import CommandBase


def start(update: Update, context: CallbackContext):
    today = datetime.datetime.now()
    current_month_bills = session.query(Bill.name, BillHistory.payment_date, BillHistory.is_paid, BillHistory.expiration_date).join(BillHistory, Bill.id == BillHistory.bill_id).filter(
        Bill.user_id == update.effective_user.id, extract('month', BillHistory.expiration_date) == today.month, extract('year', BillHistory.expiration_date) == today.year).all()

    has_bills_this_month = len(current_month_bills) == 0

    message = 'There is no bills for this month' \
        if has_bills_this_month else \
        [f'{bill[0]} was { f"not payed and expires on {bill[3]} " if bill[2] == False else f"payed in {bill[1]}" } {"✅" if bill[2] == True else "❌" }' for bill in current_month_bills]

    update.message.reply_text(message if has_bills_this_month else '\n'.join(message))


class ListBillsStatusCommand(CommandBase):

    @property
    def command_name(self):
        return 'listbillsstatus'

    @property
    def command_description(self):
        return 'This command allows you to see which bills you have paid.'

    def get_command_instance(self):
        return CommandHandler(self.command_name, start)
