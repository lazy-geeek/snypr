import pandas as pd
import datetime
import requests
import re
import time, json
from pprint import pprint

from decouple import config

base_url = "https://birdeye.so/token/"

url = "https://public-api.birdeye.so/defi/tokenlist"


def birdeye_launches():

    tokens = []
    offset = 0
    limit = 50
    total_tokens = 0
    # num_tokens = NUM_TOKENS_2SEARCH
    # mc_high = MARKET_CAP_MAX
    # mc_low = 50

    # Set minimum liquidity and minimum 24-hour volume
    # min_liquidity = MIN_LIQUIDITY
    # min_volume_24h = MIN_24HR_VOLUME
    # mins_last_trade = 59

    # THIS LOOPS AND GRABS ALL THE TOKENS TIL WE HIT MAX TOKENS
    # while total_tokens < num_tokens:
    try:
        print(f"scanning solana for new tokens, total scanned: {total_tokens}...")
        params = {
            "sort_by": "v24hChangePercent",
            "sort_type": "desc",
            "offset": offset,
            "limit": limit,
        }

        headers = {"x-chain": "solana", "X-API-KEY": config("BIRDEYE_API_KEY")}

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            response_data = response.json()
            new_tokens = response_data.get("data", {}).get("tokens", [])
            tokens.extend(new_tokens)
            total_tokens += len(new_tokens)
            offset += limit
            pprint(response_data)
        else:
            print(f"Error {response.status_code}: trying again in 10 seconds...")
            time.sleep(10)  # Sleep longer on error before retrying
            # continue  # Skip to the next pagination

        time.sleep(0.1)  # Sleep to avoid hitting rate limits
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}. Retrying in 10 seconds...")
        time.sleep(10)
        # continue


birdeye_launches()
