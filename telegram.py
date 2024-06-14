import re

from helper_functions import *

from telethon import TelegramClient, events, sync
from telethon.tl.types import MessageEntityTextUrl
from decouple import config

# Replace these with your own values
api_id = config("TELEGRAM_API_ID")
api_hash = config("TELEGRAM_API_HASH")
channel_username = config("TELEGRAM_CHANNEL_ID")
phone = config("TELEGRAM_PHONE_NO")

LIQUIDITY_MIN = 1_000


# Create the client and connect
client = TelegramClient("session_name", api_id, api_hash)


async def main():
    # Start the client
    await client.start()

    # Ensure you're authorized
    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        await client.sign_in(phone, input("Enter the code: "))

    # Get the channel entity
    channel = await client.get_entity(channel_username)

    # Define the event handler
    @client.on(events.NewMessage(chats=channel))
    async def handler(event):
        msg = event.message
        msg_text = event.message.message

        # Get values from the message
        pattern = re.compile(
            r"^(Pair|BaseToken|QuoteToken|Liquidity): (.+)$", re.MULTILINE
        )
        matches = pattern.findall(msg_text)
        values = [match[1] for match in matches]

        pair = values[0]
        base_token = values[1]
        quote_token = values[2]
        liquidity = convert_string_to_number(values[3])

        if (liquidity > LIQUIDITY_MIN) and (quote_token in ["SOL", "USDT", "USDC"]):

            for url_entity, inner_text in msg.get_entities_text(MessageEntityTextUrl):
                token_url = url_entity.url
                token = inner_text
                token_address = get_token_from_url(token_url)
                if token == base_token:

                    # token_info = birdeye_token_overview(token_address)

                    print(
                        f"{current_timestamp()} {pair} - Liquidiy: {int(liquidity):,} - {token_address}"
                    )

    # Run the client until disconnected
    await client.run_until_disconnected()


with client:
    client.loop.run_until_complete(main())
