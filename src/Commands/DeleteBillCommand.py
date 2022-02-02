from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, CallbackContext, ConversationHandler, CallbackQueryHandler
from src.Data.Database import session, Bill, BillHistory

from src.Commands.Base.CommandBase import CommandBase
from src.Utils.ReplyMarkupUtils import create_confirmation_markup_yes_or_no_options

DELETE_CONFIRMATION, DELETE_BILL, SAVE = range(2)


def start(update: Update, context: CallbackContext):
    user_bills = session.query(Bill.name, Bill.id).filter_by(user_id=update.effective_user.id).all()

    has_bills = len(user_bills) > 0

    if not has_bills:
        update.message.reply_text('You have no bills')
        return ConversationHandler.END

    bills_options = InlineKeyboardMarkup(
        [[InlineKeyboardButton(bill.name, callback_data=bill.id) for bill in user_bills]])

    context.user_data['user_bills'] = user_bills

    update.message.reply_text('Which bill do you want to delete?', reply_markup=bills_options)

    return DELETE_CONFIRMATION


def delete_confirmation_handler(update: Update, context: CallbackContext):
    bill_selected_id = int(update.callback_query.data)
    context.user_data['selected_bill_to_delete'] = bill_selected_id

    selected_bill = [bill for bill in context.user_data['user_bills'] if bill.id == int(bill_selected_id)][0]

    update.callback_query.edit_message_text(f'Are you sure you want to delete {selected_bill.name} ?',
                                            create_confirmation_markup_yes_or_no_options())

    return DELETE_BILL


def delete_bill_handler(update: Update, context: CallbackContext):
    should_delete_bill = bool(update.callback_query.data)

    update.callback_query.edit_message_reply_markup(None)

    if should_delete_bill:
        selected_bill_id = context.user_data['selected_bill_to_delete']
        session.query(BillHistory).filter(BillHistory.bill_id == selected_bill_id).delete()
        session.query(Bill).filter(Bill.id == selected_bill_id).delete()

        session.commit()

        update.callback_query.edit_message_text('Bill deleted.')
    else:
        update.callback_query.edit_message_text('Alright, the bill was not deleted.')

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
                DELETE_BILL: [CallbackQueryHandler(delete_bill_handler)],
                DELETE_CONFIRMATION: [CallbackQueryHandler(delete_confirmation_handler())]
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
