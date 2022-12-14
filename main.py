import requests
import logging

from contextlib import suppress
from time import sleep
from environs import Env
from telegram import Bot

import logging_bot


TG_LOGGER = logging.getLogger('tg_logger')


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

    logger_bot = Bot(token=env('LOG_BOT_TOKEN'))
    admin_chat_id = env('ADMIN_CHAT_ID')

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    TG_LOGGER.setLevel(logging.INFO)
    TG_LOGGER.addHandler(logging_bot.TelegramLogsHandler(logger_bot, admin_chat_id))


    devman_long_polling_url = 'https://dvmn.org/api/long_polling/'
    headers = {
        'Authorization': f"Token {env('DEVMAN_API_TOKEN')}"
    }

    user_chat_id = env('USER_CHAT_ID')
    main_bot = Bot(token=env('TELEGRAM_BOT_TOKEN'))

    connection_retry = 0
    TG_LOGGER.info('Бот запущен!')

    while True:
        with suppress(requests.exceptions.ReadTimeout):
            params = {
                'timestamp': ''
            }
            try:
                response = requests.get(
                    devman_long_polling_url,
                    headers=headers,
                    params=params
                    )
                response.raise_for_status()

                work_check_result = response.json()

                if work_check_result['status'] == 'found':
                    params['timestamp'] = work_check_result['new_attempts'][-1]['timestamp']
                    post_message(
                        main_bot,
                        work_check_result,
                        user_chat_id
                        )

                else:
                    params['timestamp'] = work_check_result['timestamp_to_request']

            except requests.exceptions.ConnectionError:
                TG_LOGGER.warning('Disconnected from the internet!')
                connection_retry += 1
                if connection_retry > 10:
                    sleep(60)

            except Exception as err:
                TG_LOGGER.warning('Got traceback!')
                TG_LOGGER.warning(err)


if __name__ == '__main__':
    main()
