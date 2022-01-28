#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to send timed Telegram messages.
This Bot uses the Updater class to handle the bot and the JobQueue to send
timed messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Alarm Bot example, sends a message after a set time.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext


from src.Commands.AddBillCommand import AddBillCommand
from src.Commands.ListBillsCommand import ListBillsCommand
from src.TelegramBot.BillsManagerBot import BillsManagerBot
from src.Data.Database import session

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def main() -> None:
    """Run bot."""

    bot = BillsManagerBot()

    bot.add_command(AddBillCommand())
    bot.add_command(ListBillsCommand())

    bot.register_handlers()

    bot.start_bot()
    # Start the Bot
    #updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    #updater.idle()


if __name__ == '__main__':
    main()