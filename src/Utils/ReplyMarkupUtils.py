from typing import Dict

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update


def create_reply_markup_options(messages_and_callbacks: Dict[str, str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(option, callback_data=messages_and_callbacks[option]) for option in
         messages_and_callbacks]
    ])


def create_confirmation_markup_true_or_false_results(yes_message: str = 'Yes', no_message: str = 'No') -> InlineKeyboardMarkup:
    return create_reply_markup_options({yes_message: 1, no_message: 0})


def get_true_or_false_markup_result(update: Update) -> bool:
    return bool(int(update.callback_query.data))
