from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

CHANNEL_ID = "@underdeathpump"

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 Analyze Token", callback_data="analyze")],
        [InlineKeyboardButton("📈 Trending Token", callback_data="trending")],
        [InlineKeyboardButton("⚙️ Help", callback_data="help")],
        [InlineKeyboardButton("👨‍💻 About Bot", callback_data="about")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📋 Main Menu:", reply_markup=reply_markup)

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = """🤖 *About This Bot*
Bot ini memberikan analisa real-time untuk token crypto multi-chain:

- ✅ Support Solana, ETH, BSC, BASE
- 🚫 Honeypot Detector (EVM)
- 📈 Chart harga 24 jam
- 🔗 Link ke DEX, Explorer, dan Social

🧠 Dev: @undrdth
🐦 [Twitter](https://x.com/LilFID12?t=cmyw-glQ3nb7zXqhA_VlDQ&s=09)
🌐 Web: https://underdeathsol.netlify.app
"""
    banner_url = "https://imgur.com/a/Akwz1jT"
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=banner_url,
        caption=msg,
        parse_mode="Markdown"
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "analyze":
        await query.edit_message_text("📨 Kirim Contract Address untuk analisa.")
    elif data == "trending":
        from analyzer import get_trending_tokens
        await get_trending_tokens(update, context)
    elif data == "help":
        await query.edit_message_text("🆘 Kirim CA (Contract Address) untuk menganalisa token.")
    elif data == "about":
        await query.edit_message_text("🤖 Analyzer Bot by UNDERDEATH\n\nDetail klik /info")
