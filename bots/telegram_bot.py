from telegram import Bot


class TelegramSender:
    def __init__(self, token: str, chat_id: str):
        self.bot = Bot(token=token)
        self.chat_id = chat_id

    async def send_product(self, name: str, discount: str, old_price: str, price: str, link: str, image_url: str):
        message = f'''
<b>🚨 {name.upper()}</b>
<b>Com {discount} de desconto:</b>

De: <s>{old_price}</s> | Por: <b>{price}</b>

<b>Link do Produto:</b>
<a href="{link}">{name}</a>
        '''
        await self.bot.send_photo(
            chat_id=self.chat_id,
            photo=image_url,
            caption=message,
            parse_mode='HTML'
        )
