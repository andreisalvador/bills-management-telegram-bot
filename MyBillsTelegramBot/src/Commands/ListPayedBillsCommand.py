from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from src.Data.Database import session, Bill, BillHistory

from src.Commands.Base.CommandBase import CommandBase

check_emoji = '\xE2\x9C\x85'


def start(update: Update, context: CallbackContext):
    bills_payed = session.query(Bill.name, BillHistory.payment_date, BillHistory.is_paid).join(BillHistory, Bill.id == BillHistory.bill_id).filter(
        Bill.user_id == str(update.effective_user.id)).all()

    message = [f'{bill[0]} was { "not" if bill[2] == False else "" }  payed in {bill[1]} {"✅" if bill[2] == True else "❌" }' for bill in bills_payed]

    update.message.reply_text('\n'.join(message))


class ListPayedBillsCommand(CommandBase):

    @property
    def command_name(self):
        return 'listpayedbills'

    @property
    def command_description(self):
        return 'This command allows you to see which bills you have paid.'

    def get_command_instance(self):
        return CommandHandler(self.command_name, start)
