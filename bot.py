import asyncio
import telegram

from environs import Env


async def main():
    env = Env()
    env.read_env()
    bot = telegram.Bot(env('TELEGRAM_BOT_TOKEN'))
    async with bot:
        message = (await bot.get_updates())[-1].message
        chat_id = message.chat_id
        await bot.send_message(
            chat_id=chat_id,
            text=f'Hello, {message.from_user.first_name}'
        )


if __name__ == '__main__':
    asyncio.run(main())
