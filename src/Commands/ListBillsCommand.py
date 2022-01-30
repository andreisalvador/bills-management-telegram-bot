from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from src.Data.Database import session, Bill

from src.Commands.Base.CommandBase import CommandBase


def start(update: Update, context: CallbackContext):
    user_bills = session.query(Bill.name, Bill.value).filter_by(user_id=update.effective_user.id).all()

    has_bills = len(user_bills) > 0

    if not has_bills:
        update.message.reply_text('You have no bills.')
    else:
        message = [f"Bill name: {bill.name} | Bill value: {bill.value}" for bill in user_bills]
        update.message.reply_text('\n'.join(message))


class ListBillsCommand(CommandBase):
    @property
    def command_name(self):
        return "listbills"

    @property
    def command_description(self):
        return "This command allows you to see all you registered bills."

    def get_command_instance(self):
        return CommandHandler(self.command_name, start)
