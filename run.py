import asyncio

from loguru import logger
from src.bot import Bot
from models import Account
from loader import config, semaphore

from art import tprint


async def start_account_safe(account: Account) -> None:
    async with semaphore:
        bot = Bot(account)
        await bot.start()


async def run() -> None:
    tprint("JamBit")
    print("Сhannel - https://t.me/JamBitPY\n\n")
    logger.info(
        f"Nyan Bot started | Version: 1.0 | Total accounts: {len(config.accounts)} | Threads: {config.threads} | Timeout between quests: {config.timeout_between_quests} sec\n\n"
    )

    tasks = [
        asyncio.create_task(start_account_safe(account)) for account in config.accounts
    ]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(run())
