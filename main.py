import logging

from src.Commands.DeleteBillCommand import DeleteBillCommand
from src.Commands.ListBillsStatusCommand import ListBillsStatusCommand
from src.Commands.PayBillCommand import PayBillCommand
from src.Commands.AddBillCommand import AddBillCommand
from src.Commands.ListBillsCommand import ListBillsCommand
from src.Schedulers.BillsHistoryScheduler import BillsHistoryScheduler
from src.TelegramBot.BillsManagerBot import BillsManagerBot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def main() -> None:
    """Run bot."""

    bot = BillsManagerBot()

    bot.add_command(AddBillCommand())
    bot.add_command(ListBillsCommand())
    bot.add_command(PayBillCommand())
    bot.add_command(ListBillsStatusCommand())
    bot.add_command(DeleteBillCommand())

    bot.add_scheduler(BillsHistoryScheduler())

    bot.register_handlers()

    bot.start_bot()


if __name__ == '__main__':
    main()
