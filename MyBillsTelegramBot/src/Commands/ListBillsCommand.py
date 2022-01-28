from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from src.Data.Database import session, Bill

from src.Commands.Base.CommandBase import CommandBase


def start(update: Update, context: CallbackContext):
    user_bills = session.query(Bill.name, Bill.value).filter_by(user_id=str(update.effective_user.id)).all()
    message = [f"Bill name: {bill.name} | Bill value: {bill.value}" for bill in user_bills]
    update.message.reply_text('\n'.join(message))


class ListBillsCommand(CommandBase):
    @property
    def command_name(self):
        return "listbills"

    @property
    def command_description(self):
        return "This command allows you to see all you registered bills."

    @property
    def is_conversation_command(self):
        return False

    def get_command_instance(self):
        return CommandHandler(self.command_name, start)
