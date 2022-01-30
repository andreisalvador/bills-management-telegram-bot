from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, CallbackContext, ConversationHandler, CallbackQueryHandler
from src.Data.Database import session, Bill, BillHistory

from src.Commands.Base.CommandBase import CommandBase

DELETE = 0


def start(update: Update, context: CallbackContext):
    user_bills = session.query(Bill.name, Bill.id).filter_by(user_id=update.effective_user.id).all()

    has_bills = len(user_bills) > 0

    if not has_bills:
        update.message.reply_text('You have no bills')
        return ConversationHandler.END

    bills_options = InlineKeyboardMarkup(
        [[InlineKeyboardButton(bill.name, callback_data=bill.id) for bill in user_bills]])

    update.message.reply_text('Which bill do you want to delete?', reply_markup=bills_options)

    return DELETE


def delete_bill(update: Update, context: CallbackContext):
    selected_bill = int(update.callback_query.data)

    update.callback_query.edit_message_reply_markup(None)

    session.query(BillHistory).filter(BillHistory.bill_id == selected_bill).delete()
    session.query(Bill).filter(Bill.id == selected_bill).delete()

    session.commit()

    update.callback_query.edit_message_text('Bill deleted.')

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text('Bye! I hope we can talk again some day.')


class DeleteBillCommand(CommandBase):
    @property
    def command_name(self):
        return 'deletebill'

    @property
    def command_description(self):
        return 'This command allows you to delete a bill.'

    def get_command_instance(self):
        return ConversationHandler(
            entry_points=[CommandHandler(self.command_name, start)],
            states={
                DELETE: [CallbackQueryHandler(delete_bill)]
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
