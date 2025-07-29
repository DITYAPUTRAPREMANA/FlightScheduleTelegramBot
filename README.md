Here is a `README.md` file for your project:

````markdown
# Flight Info Bot and Data Fetcher

This project consists of several components for retrieving, processing, and storing flight information in a database. The system fetches flight data from an external API and allows querying the data via a Telegram bot. The bot is capable of searching for flight schedules by date, flight code, and route.

## Features

- Fetch flight data from an API and store it in a MySQL database.
- A Telegram bot that allows users to query flight information, including:
  - Flight information by flight code and date.
  - Flight schedules for a specific date.
  - Flights based on origin, destination, and date.
- Flight data is stored and updated in a MySQL database, ensuring real-time flight information.

## Components

### 1. **fetch_and_store_api.py**
   - Fetches flight data from an API.
   - Inserts or updates flight data into a MySQL database.
   - Uses environment variables to store database configuration.

### 2. **flight_bot.py**
   - Handles database interactions for flight data queries.
   - Provides functions to search for flight information by flight code, date, and route.

### 3. **handler.py**
   - Defines command handlers for the Telegram bot.
   - Includes `/start`, `/help`, `/flight`, `/schedule`, and `/route` commands to interact with the bot.

### 4. **main.py**
   - Initializes the Telegram bot and sets up the command and message handlers.

### 5. **scaping.py**
   - Fetches flight data from the external API.
   - Inserts the data into the MySQL database, creating the necessary table if it does not exist.

### 6. **requirements.txt**
   - Lists the required Python libraries to run the project.
   - Includes `python-telegram-bot`, `python-dotenv`, `mysql-connector-python`, and `requests`.

### 7. **Docker Setup**
   - Docker-related files for setting up the project in a containerized environment:
     - `.dockerignore`: Specifies which files should be ignored by Docker.
     - `docker-compose.yml`: Defines the services for running the application in Docker.
     - `docker-compose.prod.yml`: Configuration for the production environment.
     - `Dockerfile`: Defines the steps to build the application image.

## Setup

### Prerequisites

1. **Python** (version 3.8 or higher)
2. **MySQL** (Ensure MySQL server is running and accessible)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/flight-info-bot.git
   cd flight-info-bot
````

2. Install the required Python libraries:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up the `.env` file with the following environment variables:

   ```
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=flight_data
   DB_PORT=3306
   BOT_TOKEN=your_telegram_bot_token
   ```

### Running the Project

1. **Start the Telegram Bot**:

   * Run the following command to start the bot:

     ```bash
     python main.py
     ```

2. **Fetch Data from API**:

   * To fetch and store data from the API, run:

     ```bash
     python scaping.py
     ```

### Docker Setup (Optional)

1. **Build and Run the Application with Docker**:

   * Use Docker Compose to build and run the application:

     ```bash
     docker-compose up --build
     ```

## Usage

Once the bot is running, you can interact with it on Telegram using the following commands:

* `/start` - Start the bot.
* `/help` - Show usage instructions.
* `/flight [flight_code] [date]` - Get information for a specific flight on a specific date.
* `/schedule [date]` - Get the flight schedule for a specific date.
* `/route [origin] [destination] [date]` - Get flights for a specific route on a specific date.

## Database Schema

The following table is used to store flight data:

```sql
CREATE TABLE IF NOT EXISTS flight_api_data (
    id INT PRIMARY KEY,
    operator VARCHAR(100),
    schedule VARCHAR(100),
    estimate VARCHAR(100),
    flightno VARCHAR(50),
    gatenumber VARCHAR(20),
    flightstat VARCHAR(50),
    fromtolocation VARCHAR(100)
);
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```

### Key Sections of the `README.md`:

1. **Project Overview**: Describes the project and its components.
2. **Features**: Lists key features like API data fetching, storing data in MySQL, and the Telegram bot capabilities.
3. **Setup Instructions**: Details steps for setting up the environment, installing dependencies, and running the project locally or via Docker.
4. **Database Schema**: Shows the database schema for the `flight_api_data` table.
5. **Docker Setup**: Describes how to use Docker to run the project.
6. **Usage Instructions**: Explains how users can interact with the Telegram bot using different commands.

You can modify the sections as needed based on your project requirements.
```
