import logging
import asyncio
import threading
import time
from dotenv import load_dotenv
from uvicorn import Config, Server
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from flight_handler import (start, flight_info, schedule_info, button, stop_monitor, monitor_flight_status, debug_monitor, test_notification, should_exit)
from config import BOT_TOKEN, LOG_LEVEL
from health import app as health_app

load_dotenv()
if BOT_TOKEN is None:
    raise ValueError("BOT_TOKEN environment variable is not set.")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def run_monitoring_loop(application):
    """Run monitoring in a separate thread with its own event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        logger.info("Starting monitoring loop in separate thread")
        loop.run_until_complete(monitor_flight_status(application))
    except Exception as e:
        logger.error(f"Monitoring loop error: {e}")
    finally:
        loop.close()

def run_health_server():
    config = Config(app=health_app, host="0.0.0.0", port=8000, log_level=LOG_LEVEL.lower())
    server = Server(config)
    asyncio.run(server.serve())


def main():
    logger.info("Starting Flight Bot...")

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("flight", flight_info))
    application.add_handler(CommandHandler("schedule", schedule_info))
    application.add_handler(CommandHandler("stop_monitor", stop_monitor))
    application.add_handler(CommandHandler("debug", debug_monitor))
    application.add_handler(CommandHandler("test", test_notification))
    application.add_handler(CallbackQueryHandler(button))

    logger.info("Starting flight monitoring thread...")
    monitoring_thread = threading.Thread(
        target=run_monitoring_loop,
        args=(application,),
        daemon=True
    )
    monitoring_thread.start()

    logger.info("🩺 Starting health server thread...")
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()

    logger.info("All systems initialized successfully!")
    print("Bot started successfully!")
    print("Flight monitoring system is active!")
    print("Health server available at /health")
    print("Debug commands available: /debug, /test")

    def run_polling_with_loop():
        """Run polling in a separate thread with its own event loop"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            logger.info("Starting polling in separate thread")
            loop.run_until_complete(application.run_polling(allowed_updates=None))
        except Exception as e:
            logger.error(f"Polling error: {e}")
        finally:
            loop.close()

    try:
        polling_thread = threading.Thread(
            target=run_polling_with_loop,
            daemon=True
        )
        polling_thread.start()
        while not should_exit:
            time.sleep(1)
        logger.info("Exit flag detected. Shutting down gracefully...")
        print("Program is shutting down...")
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        logger.info("Bot shutting down...")
        print("Program has completely stopped. Please restart with /start to begin again.")

if __name__ == '__main__':
    main()