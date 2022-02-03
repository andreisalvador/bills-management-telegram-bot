from datetime import datetime

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, \
    Filters
from src.Data.Database import session, Bill, BillHistory

from src.Commands.Base.CommandBase import CommandBase
from src.Utils.ReplyMarkupUtils import create_reply_markup_options, create_confirmation_markup_true_or_false_results, \
    get_true_or_false_markup_result

IDENTIFY_BILL_VALUE, NEW_VALUE, IDENTIFY_BILL_SITUATION, PAY_BILL = range(4)


def confirmation_message(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Can we confirm the payment?',
                             reply_markup=create_confirmation_markup_true_or_false_results())


def start(update: Update, context: CallbackContext):
    user_bills = session.query(Bill.id, Bill.name, Bill.value).join(BillHistory, BillHistory.bill_id == Bill.id).filter(
        Bill.user_id == update.effective_user.id, BillHistory.is_paid == False).all()

    if len(user_bills) == 0:
        update.message.reply_text('There is no bills to pay.')
        return ConversationHandler.END

    context.user_data['user_bills'] = user_bills

    bills_options = InlineKeyboardMarkup(
        [[InlineKeyboardButton(bill.name, callback_data=bill.id) for bill in user_bills]])
    update.message.reply_text('Select the bill that you want to pay:', reply_markup=bills_options)
    return IDENTIFY_BILL_SITUATION


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END


def identify_bill_value_handler(update: Update, context: CallbackContext):
    paid_different_value = get_true_or_false_markup_result(update)
    context.user_data['is_value_changed'] = paid_different_value

    update.callback_query.edit_message_reply_markup(None)

    message = 'Alright, you paid another value.' if paid_different_value else 'Ok, seems that nothing changed.'

    update.callback_query.edit_message_text(message)

    if paid_different_value:
        context.bot.send_message(chat_id=update.effective_chat.id, text='What is the value that you paid?')
        return NEW_VALUE

    confirmation_message(update, context)

    return PAY_BILL


def new_value_handler(update: Update, context: CallbackContext):
    context.user_data['value_paid'] = update.message.text
    confirmation_message(update, context)
    return PAY_BILL


def identify_bill_situation_handler(update: Update, context: CallbackContext):
    bill_selected_id = update.callback_query.data
    context.user_data['selected_bill_id'] = bill_selected_id
    update.callback_query.edit_message_reply_markup(None)

    selected_bill = [bill for bill in context.user_data['user_bills'] if bill.id == int(bill_selected_id)][0]

    update.callback_query.edit_message_text(f'{selected_bill.name} selected.')

    options = create_confirmation_markup_true_or_false_results('I paid a different value', 'I paid the value mentioned')

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f'You paid {selected_bill[1]} with value {selected_bill[2]} ?', reply_markup=options)
    context.user_data['value_paid'] = selected_bill[2]

    return IDENTIFY_BILL_VALUE


def pay_bill_handler(update: Update, context: CallbackContext):
    confirmed_payment = get_true_or_false_markup_result(update)

    if not confirmed_payment:
        update.callback_query.edit_message_reply_markup(None)
        update.callback_query.edit_message_text('Alright, payment process cancelled!')
        return ConversationHandler.END

    value_paid = context.user_data['value_paid']
    selected_bill_id = context.user_data['selected_bill_id']
    is_value_changed = context.user_data['is_value_changed']

    session.query(BillHistory).filter(BillHistory.bill_id == selected_bill_id).update(
        {'is_paid': True, 'payment_date': datetime.now(), 'value_payed': value_paid,
         'is_value_changed': is_value_changed})
    session.commit()

    update.callback_query.edit_message_reply_markup(None)
    update.callback_query.edit_message_text('Alright, paid!')

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
                PAY_BILL: [CallbackQueryHandler(pay_bill_handler)],
                IDENTIFY_BILL_VALUE: [CallbackQueryHandler(identify_bill_value_handler)],
                NEW_VALUE: [MessageHandler(Filters.regex(r'\d+'), new_value_handler)],
                IDENTIFY_BILL_SITUATION: [CallbackQueryHandler(identify_bill_situation_handler)],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
