import logging
from telegram.ext import ApplicationBuilder
from config import BOT_TOKEN
import handlers

def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register all handlers
    handlers.register(app)

    logging.info("Bot is polling...")
    app.run_polling()

if __name__ == "__main__":
    main()