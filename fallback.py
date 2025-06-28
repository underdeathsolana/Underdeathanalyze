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
