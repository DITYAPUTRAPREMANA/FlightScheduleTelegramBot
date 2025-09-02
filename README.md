# Flight Monitoring Telegram Bot System

## Overview

This project is a **Python-based flight information monitoring system** featuring a Telegram bot, a FastAPI health server, and real-time flight monitoring capabilities. The bot enables users to query flight schedules, monitor flight statuses, and receive instant updates via Telegram. System health is tracked through a dedicated FastAPI endpoint.

---

## Features

- Real-time flight schedule and status queries
- Continuous monitoring with instant notifications on changes (status, schedule, gate, estimate)
- Support for domestic and international flights
- User-friendly interaction via Telegram bot commands and buttons
- Concurrent operations using Python threading and asyncio
- API-based health checks with FastAPI

---

## Architecture

### Main Components

- **main.py**: Entry point. Initializes the bot, monitoring, and health server in separate threads for concurrent operation.
- **config.py**: Loads all configuration parameters and secrets (e.g., bot token, API URLs, log level) from environment variables using `dotenv`.
- **flight_bot.py**: Provides the `FlightScheduleBot` class that fetches and normalizes flight schedule data from APIs, and offers data-filtering/search utilities.
- **flight_handler.py**: Implements all Telegram bot command handlers and interaction logic; manages user sessions, monitoring states, command routing, and notification formatting.
- **health.py**: FastAPI mini-app that exposes a `/health` endpoint for system health checks.

---

## Installation

1. **Clone the repository**  
   ```bash
   git clone <repo-url>
   cd <project-directory>
   ```

2. **Set up environment variables**  
   Create a `.env` file in the project root:
   ```
   BOT_TOKEN=your-telegram-bot-token
   API_DOM_URL=your-domestic-flights-api-endpoint
   API_INTER_URL=your-international-flights-api-endpoint
   MONITOR_INTERVAL_SECONDS=10
   LOG_LEVEL=INFO
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

1. **Run the bot**  
   ```
   python main.py
   ```

2. **Interact via Telegram**:  
   - Start a conversation by sending `/start` to your Telegram bot.
   - Follow on-screen options to query flights or begin flight monitoring.
   - Use `/flight [FLIGHT_CODE]` or `/schedule [YYYYMMDD]` to get info.

3. **Monitoring & Notifications**:  
   - Select a flight to monitor. The bot will check for updates in real-time.
   - You receive notifications for any changes (status, schedule, gate).
   - Use `/stop_monitor` to stop monitoring a flight.

4. **Health Checks**:  
   Access http://localhost:8000/health to verify the system status.

---

## Project Structure

| File             | Purpose                                                                          |
|------------------|----------------------------------------------------------------------------------|
| main.py          | Launches the bot, monitoring, and health server threads                          |
| config.py        | Loads environment configuration using `dotenv`                                    |
| flight_bot.py    | Flight data fetching, normalization, and search utilities                        |
| flight_handler.py| Telegram bot command handlers and real-time flight monitoring logic               |
| health.py        | FastAPI service for health check endpoint                                        |

---

## Dependencies

- Python 3.8+
- python-telegram-bot (v20+)
- FastAPI
- uvicorn
- python-dotenv
- requests

---

## Configuration

Environment variables must be defined in a `.env` file or exported before running:

- `BOT_TOKEN` – Telegram bot API token (required)
- `API_DOM_URL` – Domestic flights API endpoint (required)
- `API_INTER_URL` – International flights API endpoint (required)
- `MONITOR_INTERVAL_SECONDS` – Monitoring interval (optional, default: 10)
- `LOG_LEVEL` – Logging level (optional, default: INFO)

---

## Contributing

Please fork the repository, create a feature branch, and open a pull request. Ensure your code follows PEP-8 and is well-documented.

---

This project provides a robust, extensible platform for flight information monitoring via Telegram, designed for real-time interaction and reliability. Configuration is environment-driven, and the architecture supports high concurrency and easy deployment.
