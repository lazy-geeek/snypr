import asyncio
import csv
import traceback
from datetime import datetime
import websockets
import time
import os
import base64
import json
from fake_useragent import UserAgent
from collections import namedtuple


def generate_sec_websocket_key():
    """Generate a random key for the Sec-WebSocket-Key header."""
    random_bytes = os.urandom(16)
    key = base64.b64encode(random_bytes).decode("utf-8")
    return key


async def dexscreener_scraper(time_interval, dex="all", page_number=1, save_file=True):
    types = ["pairs", "latestBlock"]

    # Initialize the UserAgent object
    ua = UserAgent()

    data = []
    fieldnames = [
        "chain_id",
        "dex_id",
        "pair_address",
        "token_address",
        "token_name",
        "token_symbol",
        "token_m5_buys",
        "token_m5_sells",
        "token_h1_buys",
        "token_h1_sells",
        "token_h1_to_m5_buys",
        "token_liquidity",
        "token_market_cap",
        "token_created_at",
        "token_created_since",
        "token_eti",
        "token_header",
        "token_website",
        "token_twitter",
        "token_links",
        "token_img_key",
        "token_price_usd",
        "token_price_change_h24",
        "token_price_change_h6",
        "token_price_change_h1",
        "token_price_change_m5",
    ]

    headers = {
        "Connection": "Upgrade",
        "Upgrade": "websocket",
        "Sec-WebSocket-Version": "13",
        "Sec-WebSocket-Key": generate_sec_websocket_key(),
        "User-Agent": ua.random,
        "Origin": "https://dexscreener.com",
    }

    base_uri = "wss://io.dexscreener.com/dex/screener/pairs/"
    dexFilter = f"desc&filters[chainIds][0]=solana&filters[dexIds][0]={dex}"
    if dex == "all":
        uri = f"{base_uri}{time_interval}/{page_number}?rankBy[key]=pairAge&rankBy[order]=asc&filters[chainIds][0]=solana"
    else:
        uri = f"{base_uri}{time_interval}/{page_number}?rankBy[key]=trendingScoreH6&rankBy[order]={dexFilter}"

    reconnect_attempts = 0

    while True:
        try:
            print("Attempting to connect...")
            async with websockets.connect(uri, extra_headers=headers) as websocket:
                print("Connected!")
                # Reset reconnect attempts on a successful connection
                reconnect_attempts = 0
                # Start the heartbeat task to keep the connection alive
                heartbeat_task = asyncio.create_task(send_ping(websocket))
                while True:
                    message_raw = await websocket.recv()
                    # pprint(message_raw)
                    try:
                        message = json.loads(message_raw)
                        message = (
                            message  # this is here for cuz it wont work right unless
                        )
                        # you use the below print statement instead. No idea why yet
                        # print(f"Decoded message: {message}")  # For debugging
                        _type = message.get(
                            "type", None
                        )  # Use .get() to avoid KeyError if 'type' key is missing
                        if _type is None:
                            raise ValueError("Message type is missing")
                        assert _type in types, f"Unexpected message type: {_type}"
                    except Exception as e:
                        # except (json.JSONDecodeError, AssertionError, ValueError, ConnectionClosedError) as e:
                        # print(f"Error processing message: {e}")
                        # traceback.print_exc()
                        continue  # Skip to the next message if there's an error

                    if _type == "pairs":

                        pairs = message["pairs"]

                        assert pairs
                        for pair in pairs:
                            chain_id = pair["chainId"]
                            dex_id = pair["dexId"]
                            pair_address = pair["pairAddress"]

                            assert pair_address

                            token_address = pair["baseToken"]["address"]
                            token_name = pair["baseToken"]["name"]
                            token_symbol = pair["baseToken"]["symbol"]

                            token_txns = pair["txns"]

                            token_m5_buys = token_txns["m5"]["buys"]
                            token_m5_sells = token_txns["m5"]["sells"]

                            token_h1_buys = token_txns["h1"]["buys"]
                            token_h1_sells = token_txns["h1"]["sells"]

                            token_h1_to_m5_buys = (
                                round(token_m5_buys * 12 / token_h1_buys, 2)
                                if token_m5_buys
                                else None
                            )
                            try:
                                token_liquidity = pair["liquidity"]["usd"]
                            except KeyError as liq_key_error:
                                print("****** key error ", liq_key_error)
                                token_liquidity = "0"

                            try:
                                token_market_cap = pair["marketCap"]
                            except KeyError as mkt_cap_key_error:
                                print(
                                    "********* mkt cap liq key error", mkt_cap_key_error
                                )
                                token_market_cap = "0"

                            # token_created_at_raw = pair["pairCreatedAt"]
                            token_created_at_raw = pair.get("pairCreatedAt", None)
                            token_created_at = token_created_at_raw / 1000
                            token_created_at = datetime.utcfromtimestamp(
                                token_created_at
                            )

                            now_utc = datetime.utcnow()
                            token_created_since = round(
                                (now_utc - token_created_at).total_seconds() / 60, 2
                            )

                            token_eti = pair.get("eti", False)
                            token_header = pair.get("profile", {}).get("header", False)
                            token_website = pair.get("profile", {}).get(
                                "website", False
                            )
                            token_twitter = pair.get("profile", {}).get(
                                "twitter", False
                            )
                            token_links = pair.get("profile", {}).get(
                                "linkCount", False
                            )
                            token_img_key = pair.get("profile", {}).get("imgKey", False)

                            token_price_usd = pair.get("priceUsd", 0)
                            token_price_change_h24 = pair["priceChange"]["h24"]
                            token_price_change_h6 = pair["priceChange"]["h6"]
                            token_price_change_h1 = pair["priceChange"]["h1"]
                            token_price_change_m5 = pair["priceChange"]["m5"]

                            values = [
                                chain_id,
                                dex_id,
                                pair_address,
                                token_address,
                                token_name,
                                token_symbol,
                                token_m5_buys,
                                token_m5_sells,
                                token_h1_buys,
                                token_h1_sells,
                                token_h1_to_m5_buys,
                                token_liquidity,
                                token_market_cap,
                                token_created_at,
                                token_created_since,
                                token_eti,
                                token_header,
                                token_website,
                                token_twitter,
                                token_links,
                                token_img_key,
                                token_price_usd,
                                token_price_change_h24,
                                token_price_change_h6,
                                token_price_change_h1,
                                token_price_change_m5,
                            ]

                            row = dict(zip(fieldnames, values))
                            data.append(row)

                    # print current time
                    now = datetime.now()
                    print(now)

        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed with code: {e.code}, reason: {e.reason}")
            await handle_reconnect_delay(reconnect_attempts)
            reconnect_attempts += 1
        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
            break


async def send_ping(websocket):
    """Send a ping to the server every 10 seconds to keep the connection alive."""
    try:
        while True:
            await websocket.ping()
            await asyncio.sleep(10)
    except websockets.exceptions.ConnectionClosed:
        print("Ping task: connection closed.")
        pass  # Connection closed, stop the task


async def handle_reconnect_delay(attempts):
    """Handle exponential backoff delay before attempting to reconnect."""
    delay = min(2**attempts, 60)  # Delay, max out at 60 seconds
    print(f"Reconnecting in {delay} seconds...")
    await asyncio.sleep(delay)


if __name__ == "__main__":
    # Define the named tuple type
    TimeIntervals = namedtuple("TimeIntervals", ["h24", "h6", "h1", "m5"])
    # Create an instance of the named tuple with the specified time intervals
    time_intervals = TimeIntervals(h24="h24", h6="h6", h1="h1", m5="m5")

    # Dex filter named tuple
    DexFilter = namedtuple(
        "DexFilter", ["all", "raydium", "orca", "meteora", "fluxbeam", "oneintro"]
    )
    # filter instance named tuple specifies the dex's
    dex_filter = DexFilter(
        all="all",
        raydium="raydium",
        orca="orca",
        meteora="meteora",
        fluxbeam="fluxbeam",
        oneintro="oneintro",
    )

    # Look at kwarg options
    asyncio.run(
        dexscreener_scraper(time_intervals.m5, dex=dex_filter.all, save_file=True)
    )
