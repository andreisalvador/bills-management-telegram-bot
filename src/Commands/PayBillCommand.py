from datetime import datetime

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler, CommandHandler, CallbackContext, CallbackQueryHandler
from src.Data.Database import session, Bill, BillHistory

from src.Commands.Base.CommandBase import CommandBase

PAY_BILL = 0


def start(update: Update, context: CallbackContext):
    user_bills = session.query(Bill.id, Bill.name).join(BillHistory, BillHistory.bill_id == Bill.id).filter(Bill.user_id == update.effective_user.id, BillHistory.is_paid == False).all()

    if len(user_bills) == 0:
        update.message.reply_text('There is no bills to pay.')
        return ConversationHandler.END

    context.user_data['user_bills'] = user_bills

    bills_options = InlineKeyboardMarkup(
        [[InlineKeyboardButton(bill.name, callback_data=bill.id) for bill in user_bills]])
    update.message.reply_text('Select the bill that you want to pay:', reply_markup=bills_options)
    return PAY_BILL


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END


def pay_bill_handler(update: Update, context: CallbackContext):
    bill_selected_id = update.callback_query.data
    update.callback_query.edit_message_reply_markup(None)

    selected_bill_name = [bill for bill in context.user_data['user_bills'] if bill.id == int(bill_selected_id)][0][1]
    update.callback_query.edit_message_text(f'{selected_bill_name} payed.')

    session.query(BillHistory).filter(BillHistory.bill_id == bill_selected_id).update({'is_paid': True, 'payment_date': datetime.now()})
    session.commit()
    return ConversationHandler.END


class PayBillCommand(CommandBase):
    @property
    def command_name(self):
        return 'paybill'

    @property
    def command_description(self):
        return 'This command allows you to pay a specific bill.'

    def get_command_instance(self):
        return ConversationHandler(
            entry_points=[CommandHandler(self.command_name, start)],
            states={
                PAY_BILL: [CallbackQueryHandler(pay_bill_handler)]
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
