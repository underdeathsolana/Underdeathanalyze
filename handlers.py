# handlers.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import requests

from config import CHANNEL_ID, BANNER_URL
from analyzer import honeypot_check

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 hello iam underdeath bot analyze!\n\nKetik /menu for start.")
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = """🤖 *About This Bot*

Bot ini menyediakan analisis token real-time:
- ✅ Multi-chain (Sol, ETH, BSC, Base)
- 🚫 Honeypot detector (EVM)
- 📈 24h Price chart
- 🔗 Link DEX, explorer

🧠 Built by: @undrdth
🐦 Twitter: [@Lilfid12](https://x.com/LilFID12)
🌐 Website: https://underdeathsol.netlify.app
"""
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=BANNER_URL,
        caption=msg,
        parse_mode="Markdown"
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 Analyze Token", callback_data="analyze")],
        [InlineKeyboardButton("📈 Trending Token", callback_data="trending")],
        [InlineKeyboardButton("⚙️ Help", callback_data="help")],
        [InlineKeyboardButton("👨‍💻 About Bot", callback_data="about")]
    ]
    await update.message.reply_text("📋 Main Menu:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "analyze":
        await query.edit_message_text("📨 Kirimkan Contract Address (CA).")
    elif data == "trending":
        await get_trending_tokens(update, context)
    elif data == "help":
        await query.edit_message_text("🆘 Kirim CA ke bot untuk dianalisa.")
    elif data == "about":
        await query.edit_message_text("🤖 Bot oleh UNDERDEATHSOL\n\nLihat info lengkap: /info")

async def get_trending_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.callback_query.edit_message_text("⏳ Mengambil trending token Solana...")
        res = requests.get("https://api.dexscreener.com/latest/dex/pairs/solana")
        if res.status_code != 200:
            await update.callback_query.edit_message_text("⚠️ Gagal mengambil data trending.")
            return
        data = res.json().get("pairs", [])
        top_tokens = sorted(data, key=lambda x: float(x.get("volume", {}).get("h24", 0)), reverse=True)[:5]

        msg = "*🔥 Trending Token Solana (Top 5)*\n"
        for i, t in enumerate(top_tokens, start=1):
            name = t.get("baseToken", {}).get("name", "-")
            symbol = t.get("baseToken", {}).get("symbol", "-")
            price = t.get("priceUsd", "0")
            vol = t.get("volume", {}).get("h24", "0")
            liq = t.get("liquidity", {}).get("usd", "0")
            url = t.get("url", "-")
            msg += f"\n*{i}. {name}* (`{symbol}`)\n💵 ${price} | 💧 LP: ${liq} | 📊 Vol: ${vol}\n🔗 [View Chart]({url})\n"

        await update.callback_query.edit_message_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.callback_query.edit_message_text(f"⚠️ Gagal: {e}")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ca = update.message.text.strip()
    if len(ca) < 30:
        await update.message.reply_text("❌ Contract Address tidak valid.")
        return

    await update.message.reply_text("⏳ Menganalisa token...")

    res = requests.get(f"https://api.dexscreener.com/latest/dex/search?q={ca}")
    if res.status_code != 200:
        await update.message.reply_text("⚠️ Gagal mengambil data.")
        return

    data_all = res.json().get("pairs", [])
    pair = next((p for p in data_all if p.get("chainId") in ["solana", "eth", "bsc", "base"]), None)

    if not pair:
        await update.message.reply_text("⚠️ Token tidak ditemukan.")
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
📈 Volume: `${volume}`
🏷️ FDV: `${fdv}`
🛡️ Honeypot: {honeypot_result}

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

    keyboard.append([InlineKeyboardButton("🐦 Creator", url="https://x.com/LilFID12")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)
    await context.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown", reply_markup=reply_markup)
