import requests

def is_suspected_pumpfun_or_moonshot(ca: str) -> bool:
    return len(ca.strip()) < 36 or "pump.fun" in ca.lower() or "moonshot" in ca.lower()

def search_gecko_terminal(ca: str) -> str:
    try:
        res = requests.get(f"https://api.geckoterminal.com/api/v2/search?query={ca}")
        if res.status_code != 200:
            return None
        data = res.json().get("data", [])
        if not data:
            return None
        for token in data:
            if token.get("type") == "pool":
                slug = token.get("id")
                return f"https://www.geckoterminal.com/{slug}"
        return None
    except Exception as e:
        print(f"GeckoTerminal Fallback Error: {e}")
        return None

BIRDEYE_API_KEY = "c869b756b67c429a854a773529b9c047"

def get_token_data_birdeye(address, chain='solana'):
    try:
        url = f"https://public-api.birdeye.so/defi/token_price?address={address}&chain={chain}"
        headers = {"X-API-KEY": BIRDEYE_API_KEY}
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()
            return {
                "price": data.get("data", {}).get("value"),
                "source": "Birdeye"
            }
        else:
            print(f"Birdeye API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching from Birdeye: {e}")
        return None

def get_token_data_gecko(address):
    try:
        url = f"https://api.geckoterminal.com/api/v2/networks/solana/tokens/{address}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            price = data.get("data", {}).get("attributes", {}).get("price_usd")
            return {
                "price": price,
                "source": "GeckoTerminal"
            }
        return None
    except Exception as e:
        print(f"Error fetching from Gecko: {e}")
        return None
