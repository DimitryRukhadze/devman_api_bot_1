import logging

from telegram import Bot
from environs import Env


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, tg_chat_id):
        super().__init__()
        self.chat_id = tg_chat_id
        self.bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(chat_id=self.chat_id, text=log_entry)


def create_logger(log_bot, admin_chat_id):
    tg_logger = logging.getLogger('tg_logger')
    tg_logger.setLevel(logging.INFO)
    tg_handler = TelegramLogsHandler(log_bot, admin_chat_id)
    tg_logger.addHandler(tg_handler)

    return tg_logger


if __name__ == '__main__':
    env = Env()
    env.read_env()

    logger_bot = Bot(token=env('LOG_BOT_TOKEN'))
    admin_chat_id = env('ADMIN_CHAT_ID')
    admin_logger = create_logger(logger_bot, admin_chat_id)
    admin_logger.info("It's alive!")