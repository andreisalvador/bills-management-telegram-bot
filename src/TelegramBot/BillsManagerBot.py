from telegram import Update
from telegram.ext import CallbackContext, Updater, CommandHandler
import os


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        'Olá, aqui você pode adicionar gerencias suas contas. Digite /commands para ver o que você pode fazer!')


class BillsManagerBot:
    def __init__(self):
        self.__commands_registered = []
        self.__updater = Updater(os.environ['TELEGRAM_BOT_TOKEN'])

    def __commands(self, update: Update, context: CallbackContext) -> None:
        commands_descriptions = {}


        for command in self.__commands_registered:
            commands_descriptions[f'/{command.command_name}'] = command.command_description

        message = '\n'.join(' - '.join((key, val)) for (key, val) in commands_descriptions.items())
        update.message.reply_text(message)

    def register_handlers(self):
        self.__updater.dispatcher.add_handler(CommandHandler("start", start))
        self.__updater.dispatcher.add_handler(CommandHandler("commands", self.__commands))

        for command in self.__commands_registered:
            self.__updater.dispatcher.add_handler(command.get_command_instance())

    def add_command(self, new_command):
        self.__commands_registered.append(new_command)

    def start_bot(self):
        self.__updater.start_polling()
        self.__updater.idle()
