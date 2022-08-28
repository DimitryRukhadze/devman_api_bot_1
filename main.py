import requests
import logging

from contextlib import suppress
from time import sleep

from environs import Env
from telegram import Bot


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, tg_chat_id):
        super().__init__()
        self.chat_id = tg_chat_id
        self.bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        return self.bot.send_message(chat_id=self.chat_id, text=log_entry)


def post_message(bot, response, chat_id):
    check_result = response["new_attempts"][-1]
    message = f'''У вас проверили работу "{check_result["lesson_title"]}".
    Вот ссылка на этот урок: {check_result["lesson_url"]}.\n'''

    if check_result['is_negative']:
        message += '\nК сожалению в работе нашлись ошибки'
    else:
        message += '\nПреподавателю всё понравилось! Можете приступать к следующему уроку'

    bot.send_message(
        chat_id=chat_id,
        text=message
    )


def main():
    env = Env()
    env.read_env()

    devman_long_polling_url = 'https://dvmn.org/api/long_polling/'
    headers = {
        'Authorization': f"Token {env('DEVMAN_API_TOKEN')}"
    }

    user_chat_id=env('USER_CHAT_ID')

    bot = Bot(token=env('TELEGRAM_BOT_TOKEN'))

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    tg_logger = logging.getLogger('tg_logger')
    tg_logger.setLevel(logging.WARNING)
    tg_handler = TelegramLogsHandler(bot, user_chat_id)
    tg_logger.addHandler(tg_handler)

    connection_retry = 0
    tg_logger.info('Бот запущен!')
    while True:
        with suppress(requests.exceptions.ReadTimeout):
            params = {
                'timestamp': ''
            }
            try:
                response = requests.get(devman_long_polling_url, headers=headers, params=params)
                response.raise_for_status()

                work_check_result = response.json()

                if work_check_result['status'] == 'found':
                    params['timestamp'] = work_check_result['new_attempts'][-1]['timestamp']
                    post_message(bot, work_check_result, user_chat_id)

                else:
                    params['timestamp'] = work_check_result['timestamp_to_request']
                    tg_logger.info('Another round!')
            except requests.exceptions.ConnectionError:
                tg_logger.warning('Disconnected from the internet!')
                connection_retry += 1
                if connection_retry > 10:
                    sleep(60)

if __name__ == '__main__':
    main()