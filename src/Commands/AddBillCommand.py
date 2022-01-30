import enum

from src.Commands.Base.CommandBase import CommandBase
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CommandHandler, CallbackContext, MessageHandler, Filters, \
    CallbackQueryHandler

from src.Data.Database import session, Bill

from src.Enums.PeriodEnum import PeriodEnum
from src.Utils.BillsUtils import create_new_bill_history

BILL_NAME, BILL_VALUE, EXPIRATION_PERIOD, EXPIRATION_DAY, SAVE = range(5)
logger = logging.getLogger(__name__)


def add_bill_cancel(update: Update, context: CallbackContext):
    update.message.reply_text('Bye! I hope we can talk again some day.')


def add_bill_start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Please, inform the bill name')
    return BILL_NAME


def finish(update: Update, context: CallbackContext):
    update.message.reply_text("Alright, saved!")
    update.message.reply_text("Thanks, see you soon!")


class AddBillCommand(CommandBase):
    @property
    def command_description(self):
        return 'This command create new bills to your list of bills to manage them later.'

    @property
    def command_name(self):
        return "addbill"

    def __init__(self):
        self.bill_name = ''
        self.bill_value = 0
        self.expiration_day = 1
        self.expiration_period = PeriodEnum.Monthly

    def create_new_bill(self, user_id) -> Bill:
        return Bill(name=self.bill_name, value=self.bill_value, expiration_day=self.expiration_day,
                    expiration_period=self.expiration_period, user_id=user_id)

    def get_adding_confirmation_message(self) -> str:
        return f'You are adding {self.bill_name} with a value of {self.bill_value}, expiration period {self.expiration_period.name} and expiration day {self.expiration_day}, right? '

    def set_bill_name_handler(self, update: Update, context: CallbackContext):
        self.bill_name = update.message.text
        update.message.reply_text('Please, inform the bill value')
        return BILL_VALUE

    def set_bill_value_handler(self, update: Update, context: CallbackContext):
        answers = InlineKeyboardMarkup([
            [InlineKeyboardButton(PeriodEnum.Monthly.name, callback_data=str(PeriodEnum.Monthly.value))],
            [InlineKeyboardButton(PeriodEnum.Quarterly.name, callback_data=str(PeriodEnum.Quarterly.value))],
            [InlineKeyboardButton(PeriodEnum.Semiannual.name, callback_data=str(PeriodEnum.Semiannual.value))]
        ])
        self.bill_value = update.message.text
        update.message.reply_text('Please, inform the expiration period', reply_markup=answers)
        return EXPIRATION_PERIOD

    def set_expiration_period_handler(self, update: Update, context: CallbackContext):
        self.expiration_period = PeriodEnum(int(update.callback_query.data))
        update.callback_query.edit_message_reply_markup(None)
        update.callback_query.edit_message_text(f'{self.expiration_period.name} selected.')
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please, inform the expiration day"
        )
        return EXPIRATION_DAY

    def set_expiration_day_handler(self, update: Update, context: CallbackContext):
        answers = InlineKeyboardMarkup([
            [InlineKeyboardButton('Yes', callback_data='True')],
            [InlineKeyboardButton('No', callback_data='False')]
        ])
        self.expiration_day = update.message.text
        update.message.reply_text(self.get_adding_confirmation_message(), reply_markup=answers)
        return SAVE

    def save_new_bill(self, update: Update, context: CallbackContext):
        update.callback_query.edit_message_reply_markup(None)

        if update.callback_query.data == 'True':
            new_bill = self.create_new_bill(update.effective_user.id)
            session.add(new_bill)
            session.flush()

            session.add(create_new_bill_history(new_bill))
            session.flush()

            session.commit()

            update.callback_query.edit_message_text('Alright, saved!')
        else:
            update.callback_query.edit_message_text('Alright, cancelled.')

        return ConversationHandler.END

    def get_command_instance(self):
        return ConversationHandler(
            entry_points=[CommandHandler(self.command_name, add_bill_start)],
            states={
                BILL_NAME: [MessageHandler(Filters.text, self.set_bill_name_handler)],
                BILL_VALUE: [MessageHandler(Filters.text, self.set_bill_value_handler)],
                EXPIRATION_PERIOD: [CallbackQueryHandler(self.set_expiration_period_handler)],
                EXPIRATION_DAY: [MessageHandler(Filters.text, self.set_expiration_day_handler)],
                SAVE: [CallbackQueryHandler(self.save_new_bill)]
            },
            fallbacks=[CommandHandler('cancel', add_bill_cancel)],
        )
