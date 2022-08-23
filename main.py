import requests

from contextlib import suppress
from environs import Env

import asyncio
import telegram


async def post_message(bot, response):
    check_results = response["new_attempts"][-1]
    message = f'''У вас проверили работу "{check_results["lesson_title"]}".
    Вот ссылка на этот урок: {check_results["lesson_url"]}.\n'''

    if check_results['is_negative']:
        message += '\nК сожалению в работе нашлись ошибки'
    else:
        message += '\nПреподавателю всё понравилось! Можете приступать к следующему уроку'

    async with bot:
        chat_id = (await bot.get_updates())[-1].message.chat_id
        await bot.send_message(
            chat_id=chat_id,
            text=message
        )


async def main():
    env = Env()
    env.read_env()

    devman_long_polling_url = 'https://dvmn.org/api/long_polling/'
    headers = {
        'Authorization': f"Token {env('DEVMAN_API_TOKEN')}"
    }
    bot = telegram.Bot(env('TELEGRAM_BOT_TOKEN'))

    while True:
        with suppress(requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
            params = {
                'timestamp': ''
            }
            response = requests.get(devman_long_polling_url, headers=headers, params=params)
            response.raise_for_status()

            decoded_response = response.json()

            if decoded_response['status'] == 'found':
                await post_message(bot, decoded_response)

            else:
                params['timestamp'] = decoded_response['timestamp_to_request']


if __name__ == '__main__':
    asyncio.run(main())