# analyzer.py

import requests

def honeypot_check(ca, chain):
    if chain.lower() not in ["eth", "bsc", "base"]:
        return "❌ Honeypot Comingsoon."
    try:
        url = f"https://api.honeypot.is/v1/Token?address={ca}&chain={chain}"
        res = requests.get(url)
        if res.status_code != 200:
            return "⚠️ Gagal mengakses Honeypot API."

        result = res.json()
        is_honey = result.get("honeypotResult", {}).get("isHoneypot", False)
        tax = result.get("simulationResult", {}).get("buyTax", 0)

        return f"🚨 Honeypot! (Buy Tax: {tax}%)" if is_honey else f"✅ Aman (Buy Tax: {tax}%)"
    except Exception as e:
        return f"⚠️ Error: {str(e)}"
