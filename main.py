import requests

from contextlib import suppress

from environs import Env
from telegram import Bot


def post_message(bot, response, chat_id):
    check_results = response["new_attempts"][-1]
    message = f'''У вас проверили работу "{check_results["lesson_title"]}".
    Вот ссылка на этот урок: {check_results["lesson_url"]}.\n'''

    if check_results['is_negative']:
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

    while True:
        with suppress(requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
            params = {
                'timestamp': ''
            }
            response = requests.get(devman_long_polling_url, headers=headers, params=params)
            response.raise_for_status()

            decoded_response = response.json()

            if decoded_response['status'] == 'found':
                params['timestamp'] = decoded_response['new_attempts'][-1]['timestamp']
                post_message(bot, decoded_response, user_chat_id)

            else:
                params['timestamp'] = decoded_response['timestamp_to_request']


if __name__ == '__main__':
    main()