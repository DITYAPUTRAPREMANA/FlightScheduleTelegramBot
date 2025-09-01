import os
from dotenv import load_dotenv

load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
API_DOM_URL = os.getenv("API_DOM_URL")
API_INTER_URL = os.getenv("API_INTER_URL")

MONITOR_INTERVAL_SECONDS = int(os.getenv("MONITOR_INTERVAL_SECONDS", "10"))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

