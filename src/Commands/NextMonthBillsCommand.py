import datetime

from dateutil.relativedelta import relativedelta

from sqlalchemy import extract
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from src.Data.Database import session, Bill, BillHistory

from src.Commands.Base.CommandBase import CommandBase


def start(update: Update, context: CallbackContext):
    today = datetime.datetime.now() + relativedelta(months=1)
    next_month_bills_history = session.query(Bill.name, BillHistory.payment_date, BillHistory.is_paid,
                                             BillHistory.expiration_date) \
        .join(BillHistory, Bill.id == BillHistory.bill_id) \
        .filter(Bill.user_id == update.effective_user.id,
                BillHistory.is_paid == False,
                extract('month', BillHistory.expiration_date) == today.month,
                extract('year', BillHistory.expiration_date) == today.year).all()

    if len(next_month_bills_history) == 0:
        update.message.reply_text('There is no bills for next month.')
    else:
        message = [
            f'{bill[0]} was {f"not payed and expires on {bill[3]} " if bill[2] == False else f"payed in {bill[1]}"} {"✅" if bill[2] == True else "❌"}'
            for bill in next_month_bills_history]

        update.message.reply_text('\n'.join(message))


class NextMonthBillsCommand(CommandBase):
    @property
    def command_name(self):
        return 'nextmonthbills'

    @property
    def command_description(self):
        return 'This command allows you to see the next month bills.'

    def get_command_instance(self):
        return CommandHandler(self.command_name, start)
