from datetime import datetime

from sqlalchemy import extract
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from src.Data.Database import session, Bill, BillHistory

from src.Commands.Base.CommandBase import CommandBase


def start(update: Update, context: CallbackContext):
    current_month = datetime.now().month
    bills_details = session.query(Bill.name, Bill.value, BillHistory.is_paid, BillHistory.value_payed) \
        .join(Bill, BillHistory.bill_id == Bill.id) \
        .filter(Bill.user_id == update.effective_user.id,
                extract('month', BillHistory.expiration_date) == current_month).all()

    if len(bills_details) == 0:
        update.message.reply_text('There is no data to be displayed.')
    else:
        message = ['   Name    |    Value 💰   |    Paid    |    Value Paid  💸 ']
        message += ['--------------------------------------------------------------------------']
        message += [f'📄 {bill[0]} |    ${bill[1]}    |   {"✅" if bill[2] else "❌"}    |     ${bill[3]} '
                  for bill in bills_details]

        message += ['---------------------------------------------------------------------------']
        message += [f'💰 Total estimated: {sum(bill[1] for bill in bills_details)} | 💸 Total paid: {sum(bill[3] for bill in bills_details)}']
        message += ['---------------------------------------------------------------------------']
        message += [f'🤑 Leftovers (estimated - paid): {sum(bill[1] - bill[3] if bill[3] > 0 else 0 for bill in bills_details)}']

        update.message.reply_text('\n'.join(message))


class QuickMonthlyReportCommand(CommandBase):
    @property
    def command_name(self):
        return 'quickmonthlyreport'

    @property
    def command_description(self):
        return 'This command allows you to see the total cost of your bills.'

    def get_command_instance(self):
        return CommandHandler(self.command_name, start)
