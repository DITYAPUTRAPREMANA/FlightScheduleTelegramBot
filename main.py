import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handler import start, help_command, flight_info, schedule_info, route_info, handle_message
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if BOT_TOKEN is None:
    raise ValueError("BOT_TOKEN environment variable is not set.")
# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("flight", flight_info))
    application.add_handler(CommandHandler("schedule", schedule_info))
    application.add_handler(CommandHandler("route", route_info))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🚀 Bot started successfully!")
    application.run_polling(allowed_updates=None)

if __name__ == '__main__':
    main()