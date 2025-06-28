from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import requests
from fallback import is_suspected_pumpfun_or_moonshot, search_gecko_terminal

CHANNEL_ID = "@underdeathpump"

def honeypot_check(ca, chain):
    if chain.lower() not in ["eth", "bsc", "base"]:
        return "❌ Honeypot Coming Soon."
    try:
        url = f"https://api.honeypot.is/v1/Token?address={ca}&chain={chain}"
        res = requests.get(url)
        if res.status_code != 200:
            return "⚠️ Gagal akses Honeypot API."
        result = res.json()
        is_honey = result.get("honeypotResult", {}).get("isHoneypot", False)
        tax = result.get("simulationResult", {}).get("buyTax", 0)
        return f"🚨 Honeypot! (Buy Tax: {tax}%)" if is_honey else f"✅ Aman (Buy Tax: {tax}%)"
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ca = update.message.text.strip()
    if len(ca) < 30:
        await update.message.reply_text("❌ Contract Address tidak valid.")
        return

    await update.message.reply_text("⏳ Analyzing...")

    url = f"https://api.dexscreener.com/latest/dex/search?q={ca}"
    res = requests.get(url)

    if res.status_code != 200:
        await update.message.reply_text("⚠️ Gagal ambil data.")
        return

    data_all = res.json().get("pairs", [])
    pair = next((p for p in data_all if p.get("chainId") in ["solana", "eth", "bsc", "base"]), None)

    if not pair:
        if is_suspected_pumpfun_or_moonshot(ca):
            fallback_url = search_gecko_terminal(ca)
            if fallback_url:
                await update.message.reply_text(f"⚠️ Token tidak terdeteksi di DexScreener.\n🔗 [View on GeckoTerminal]({fallback_url})", parse_mode="Markdown")
                return
        await update.message.reply_text("⚠️ Token tidak ditemukan di chain yang didukung.")
        return

    chain = pair.get("chainId")
    name = pair.get("baseToken", {}).get("name", "-")
    symbol = pair.get("baseToken", {}).get("symbol", "-")
    price = pair.get("priceUsd", "0")
    fdv = pair.get("fdv", "0")
    liq = pair.get("liquidity", {}).get("usd", "0")
    volume = pair.get("volume", {}).get("h24", "0")
    dex_url = pair.get("url", "-")

    honeypot_result = honeypot_check(ca, chain)

    msg = f"""📊 *Token Analyzer by UnderdeathPump*
🌐 Chain: `{chain.upper()}`
🔹 Name: `{name}`
🔹 Symbol: `{symbol}`
💵 Price: `${price}`
💧 LP: `${liq}`
📈 Volume (24h): `${volume}`
🏷️ FDV: `${fdv}`
🛡️ Honeypot Check: {honeypot_result}

📍 CA: `{ca}`"""

    keyboard = [[InlineKeyboardButton("🔗 DexScreener", url=dex_url)]]

    if chain == "solana":
        keyboard += [
            [InlineKeyboardButton("💱 Raydium", url=f"https://raydium.io/swap/?inputCurrency=sol&outputCurrency={ca}")],
            [InlineKeyboardButton("🤖 Maestro", url=f"https://t.me/maestro?start=r-undrdth-{ca}")],
            [InlineKeyboardButton("🛡️ Trojan", url=f"https://t.me/solana_trojanbot?start=r-undrdth-{ca}")],
            [InlineKeyboardButton("⚔️ GMGN", url=f"https://t.me/gmgnaibot?start=r-i_5RkcycHD-{ca}")],
            [InlineKeyboardButton("🧾 SolScan", url=f"https://solscan.io/token/{ca}")]
        ]
    else:
        explorer = {
            "bsc": "bscscan.com",
            "eth": "etherscan.io",
            "base": "basescan.org"
        }.get(chain, "etherscan.io")
        keyboard.append([InlineKeyboardButton("🧾 Explorer", url=f"https://{explorer}/token/{ca}")])

    keyboard.append([InlineKeyboardButton("🐦 Creator: @Lilfid12", url="https://x.com/LilFID12")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)
    await context.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown", reply_markup=reply_markup)

async def get_trending_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.callback_query.edit_message_text("⏳ Mengambil data trending token Solana...")
        res = requests.get("https://api.dexscreener.com/latest/dex/pairs/solana")
        if res.status_code != 200:
            await update.callback_query.edit_message_text("⚠️ Gagal mengambil data.")
            return
        data = res.json().get("pairs", [])
        top_tokens = sorted(data, key=lambda x: float(x.get("volume", {}).get("h24", 0)), reverse=True)[:5]

        msg = "*🔥 Trending Token Solana (Top 5 by 24h Volume)*\n"
        for i, t in enumerate(top_tokens, 1):
            name = t.get("baseToken", {}).get("name", "-")
            symbol = t.get("baseToken", {}).get("symbol", "-")
            price = t.get("priceUsd", "0")
            vol = t.get("volume", {}).get("h24", "0")
            liq = t.get("liquidity", {}).get("usd", "0")
            url = t.get("url", "-")
            msg += f"\n*{i}. {name}* (`{symbol}`)\n💵 ${price} | 💧 LP: ${liq} | 📊 Vol: ${vol}\n🔗 [View Chart]({url})\n"

        await update.callback_query.edit_message_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.callback_query.edit_message_text(f"⚠️ Error: {e}")
