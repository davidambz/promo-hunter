import asyncio
from dotenv import dotenv_values
from bots.telegram_bot import TelegramSender
from scrapers.kabum import run_kabum_scraper

config = dotenv_values(".env")


async def main():
    bot = TelegramSender(token=config['TELEGRAM_TOKEN'], chat_id=config['CHAT_ID'])
    await run_kabum_scraper(
        telegram_sender=bot,
        url=config['LINK_SITE'],
        csv_path='data/sent_products.csv'
    )


if __name__ == "__main__":
    asyncio.run(main())
