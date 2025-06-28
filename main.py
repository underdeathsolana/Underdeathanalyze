from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
import os
import logging
from dotenv import load_dotenv
import nest_asyncio

nest_asyncio.apply()

from handlers import menu, info, button_callback
from analyzer import analyze

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await menu(update, context)

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("menu", menu))
app.add_handler(CommandHandler("info", info))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze))
app.add_handler(CallbackQueryHandler(button_callback))

print("🤖 Bot sedang berjalan...")
app.run_polling()
