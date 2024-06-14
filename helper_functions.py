import requests, json


from decouple import config
from pprint import pprint
from datetime import datetime


def convert_string_to_number(value_str):
    value_str = value_str.strip()  # Remove leading/trailing whitespace
    multiplier = 1

    if value_str.endswith("K"):
        multiplier = 1_000
        value_str = value_str[:-1]  # Remove the 'K'
    elif value_str.endswith("M"):
        multiplier = 1_000_000
        value_str = value_str[:-1]  # Remove the 'M'

    # Remove any currency symbols
    value_str = value_str.replace("$", "").replace(",", "")

    # Check if the remaining string is numeric
    if not value_str or not any(char.isdigit() for char in value_str):
        return 0

    # Convert to float and apply the multiplier
    try:
        number = float(value_str) * multiplier
    except ValueError:
        return 0

    return number


def get_token_from_url(url):
    return url.split("/")[-1]


def birdeye_token_overview(token_address):

    url = "https://public-api.birdeye.so/defi/token_overview"

    headers = {
        "accept": "application/json",
        "x-chain": "solana",
        "X-API-KEY": config("BIRDEYE_API_KEY"),
    }

    params = {"address": token_address}

    response = requests.get(url, headers=headers, params=params)

    pprint(response)

    if response.status_code == 200:
        return response.json()


def current_timestamp():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")
