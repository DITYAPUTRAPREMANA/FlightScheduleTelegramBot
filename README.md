Here is a `README.md` for your project based on the files provided:

---

# Flight Information Monitoring Bot

This project is a flight monitoring bot that provides real-time updates on flight schedules and statuses. It integrates with Telegram, allowing users to monitor both domestic and international flights. The bot fetches data from APIs and sends notifications when there are updates to the flight statuses, schedules, or gates.

## Features

* **Flight Monitoring**: Users can monitor specific flights by flight number.
* **Real-time Notifications**: The bot sends notifications when there are updates such as delays, cancellations, or gate changes.
* **Flight Schedule Lookup**: Users can search for flight schedules by date and flight type (domestic or international).
* **Multi-language Support**: The bot supports English and Bahasa Indonesia, with language preference selection.
* **Health Monitoring**: A health check endpoint is available to ensure the bot's API is functioning properly.

## Requirements

* Python 3.8+
* `requests` library
* `python-dotenv` for environment variable management
* `python-telegram-bot` for Telegram integration
* `FastAPI` for health check endpoint
* `Uvicorn` for serving the FastAPI health check endpoint

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your `.env` file:

   * The `.env` file should include the following:

     ```bash
     BOT_TOKEN=<Your-Telegram-Bot-Token>
     API_DOM_URL=<Your-Domestic-Flight-API-URL>
     API_INTER_URL=<Your-International-Flight-API-URL>
     MONITOR_INTERVAL_SECONDS=10
     LOG_LEVEL=INFO
     ```

4. Start the bot:

   ```bash
   python main.py
   ```

   This will:

   * Start the flight monitoring loop.
   * Start the health check server on `http://localhost:8000/health`.

5. Start monitoring flights by interacting with the bot on Telegram.

## Key Components

### `flight_bot.py`

Contains the `FlightScheduleBot` class, which handles the interaction with the flight APIs. It fetches flight data, normalizes it, and provides methods to retrieve flight details for specific dates and flight codes.

### `flight_handler.py`

Handles the main logic for the bot, including user interactions via Telegram commands and callback queries. It manages the state of flight monitoring, such as starting and stopping monitoring, handling schedules, and sending notifications.

### `main.py`

This is the entry point for the bot. It sets up the Telegram bot, runs the monitoring system in a separate thread, and starts the health server. It also manages the polling of Telegram updates.

### `health.py`

Provides a health check endpoint using FastAPI. It responds with a status of `"ok"` when the bot is running correctly.

### `config.py`

Contains the configuration for the bot, including the environment variables for the API URLs, bot token, and logging level.

### `.env`

Contains environment variables used for the configuration, such as the bot token and API URLs.

## Usage

1. **Start the bot**:

   * Use `/start` to begin the interaction with the bot.
   * Select the flight type (domestic or international).
   * Monitor flight statuses by using the "Start Monitoring" button.

2. **Monitor Flight**:

   * The bot will send real-time notifications for status updates such as delays or cancellations.

3. **Stop Monitoring**:

   * To stop monitoring a flight, use `/stop_monitor`.

4. **Check Flight Information**:

   * Use `/flight <flight_code>` to get details of a specific flight.

5. **Check Flight Schedules**:

   * Use `/schedule <date>` to view available flights for a given date.

6. **Change Language**:

   * Use `/language` to change the language preference between English and Bahasa Indonesia.

7. **Health Check**:

   * Access the health check endpoint at `/health` to ensure the bot is running.

## Logging

The bot logs detailed information about its operations. Logs are generated based on the level specified in the `.env` file (`LOG_LEVEL`), which can be adjusted to control the verbosity of logs.

## Contributing

Feel free to fork the repository and submit pull requests for any improvements, bug fixes, or new features.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

This should give a clear overview of the project. Let me know if you'd like any adjustments!
