Based on the files you've uploaded, I can help you create a README for your project. Below is a suggested structure for the `README.md` file:

---

# Flight Schedule Bot

A simple Telegram bot designed to help users check flight schedules, flight details, and routes. The bot connects to a MySQL database to fetch flight data and provides users with flight-related information using several commands.

## Features

* **Flight Information:** Get details of a specific flight based on the flight code and date.
* **Schedule:** View available flights on a specific date.
* **Route Search:** Find flights based on origin, destination, and date.
* **Help Command:** Get assistance on how to use the bot.

## Installation

### Prerequisites

* Python 3.8+
* MySQL Server
* Telegram bot token from [BotFather](https://core.telegram.org/bots#botfather)

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/TelegramBotChat.git
cd TelegramBotChat
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the root directory and add the following:

```env
BOT_TOKEN=your-telegram-bot-token
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your-database-password
DB_NAME=flight_schedule
DB_PORT=3306
```

### 4. Start the bot

```bash
python bot.py
```

The bot should now be running, and you can interact with it on Telegram.

## Commands

1. `/flight [flight_code] [date]` - Get information about a specific flight.

   * Example: `/flight GA123 2024-07-20`

2. `/schedule [date]` - Get the schedule of flights on a specific date.

   * Example: `/schedule 2024-07-20`

3. `/route [origin] [destination] [date]` - Search for flights between two airports on a specific date.

   * Example: `/route CGK DPS 2024-07-20`

4. `/help` - Displays information on how to use the bot.

## Database Structure

The bot interacts with a MySQL database. The schema should contain the following tables:

* **flights** - Contains flight information (flight\_code, departure\_time, arrival\_time, etc.)
* **airports** - Contains airport details (code, city, name)
* 
* **airlines** - Contains airline details (name)

Make sure the database is populated with flight data.

## Logging

The bot logs information and errors using Python's `logging` library. You can check the logs for debugging if needed.

## Contributing

Feel free to fork this repository and submit pull requests. We welcome contributions and suggestions to improve the bot.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

This README provides an overview of the bot, setup instructions, and usage details. You can replace `yourusername` with your actual GitHub username in the repository URL. Let me know if you need any additional changes or details!
