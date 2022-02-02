from typing import Dict

from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def create_reply_markup_options(messages_and_callbacks: Dict[str, str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(option, callback_data=messages_and_callbacks[option]) for option in
         messages_and_callbacks]
    ])
