from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from flight_bot import FlightScheduleBot
import asyncio
import logging
import traceback
from config import MONITOR_INTERVAL_SECONDS

logger = logging.getLogger(__name__)
flight_bot = FlightScheduleBot()

monitored_flights = {}
should_exit = False

def is_user_monitoring(user_id):
    """Check if user is currently monitoring a flight"""
    return user_id in monitored_flights

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_user_monitoring(user_id):
        await update.message.reply_text(
            "⚠️ You are currently monitoring a flight. Please stop monitoring first using /stop_monitor before using other commands.."
        )
        return
    welcome_message = """
🛫 *Hello Passenger, Welcome to Flight Info Bot!*

I can help you find flight schedule information in real-time 😉

*Please select the type of flights you want to monitor:*
    """
    keyboard = [
        [
            InlineKeyboardButton("International", callback_data='I'),
            InlineKeyboardButton("Domestic", callback_data='D')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    choice = query.data
    user_id = query.from_user.id

    await query.answer()
    if is_user_monitoring(user_id) and not choice.startswith("stop_monitor_"):
        await query.edit_message_text(
            "⚠️ You are currently monitoring a flight. Please stop monitoring first using /stop_monitor before using other commands.."
        )
        return
    if choice in ['I', 'D']:
        context.user_data['flight_type'] = choice
        flight_type_name = "International" if choice == 'I' else "Domestic"

        from datetime import timedelta
        today = datetime.now()
        keyboard = [
            [
                InlineKeyboardButton("📅 Schedule", callback_data=f"schedule_{choice}_{today.strftime('%Y-%m-%d')}"),
                InlineKeyboardButton("🔍 Search Flight", callback_data=f"search_flight_{choice}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=f"✅ You selected to monitor {flight_type_name.lower()} flights.\n\n"
                 f"🛫 What would you like to do?\n\n"
                 f"• View flight schedules\n"
                 f"• Search for a specific flight",
            reply_markup=reply_markup
        )

    elif choice.startswith("monitor_"):
        flight_id = choice.split('_')[1]
        logger.info(f"Attempting to monitor flight with ID: {flight_id}")
        flight_info = flight_bot.get_flight_info_by_id(flight_id)
        logger.info(f"Flight info retrieved: {flight_info is not None}")
        if flight_info:
            monitored_flights[user_id] = {
                'flight_id': flight_id,
                'last_status': flight_info['flightstat'],
                'last_schedule': str(flight_info['schedule']) if flight_info['schedule'] else None,
                'last_estimate': str(flight_info['estimate']) if flight_info['estimate'] else None,
                'last_gate': str(flight_info['gatenumber']) if flight_info['gatenumber'] else None,
                'flight_no': flight_info['flightno'],
                'last_seen': datetime.now(),
                'notification_count': 0,
                'check_count': 0,
                'last_message_id': None
            }

            logger.info(f"User {user_id} started monitoring flight {flight_info['flightno']} (ID: {flight_id})")
            logger.info(f"Initial monitoring data: {monitored_flights[user_id]}")

            keyboard = [
                [InlineKeyboardButton("🚫 Stop Monitoring", callback_data="stop_monitoring")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            sent_message = await query.edit_message_text(
                f"✅ You are now monitoring flight {flight_info['flightno']}!\n\n"
                f"📊 Current Status: {flight_info['flightstat']}\n"
                f"⏰ Schedule: {flight_info['schedule']}\n"
                f"🕐 Estimate: {flight_info['estimate']}\n"
                f"🚪 Gate: {flight_info['gatenumber']}\n\n"
                "🔔 You will receive notifications when the status or timing changes.\n\n"
                "💡 Monitoring system will check for updates every 10 seconds.",
                reply_markup=reply_markup
            )
            if sent_message:
                monitored_flights[user_id]['last_message_id'] = sent_message.message_id

    elif choice.startswith("stop_monitor_"):
        flight_id = choice.split('_')[-1]
        if user_id in monitored_flights:
            flight_no = monitored_flights[user_id].get('flight_no', flight_id)
            del monitored_flights[user_id]
            logger.info(f"User {user_id} stopped monitoring flight {flight_no}")
            await query.edit_message_text(
                f"🚫 You have stopped monitoring flight {flight_no}.\n\n"
                "✅ You can now use all bot commands again. Type /start to begin."
            )
        else:
            await query.edit_message_text(
                "❌ No active monitoring found."
            )

    elif choice.startswith("schedule_"):
        parts = choice.split('_')
        if len(parts) >= 3:
            flight_type = parts[1]
            date_str = parts[2]
            await handle_schedule_request(query, flight_type, date_str, user_id)

    elif choice.startswith("search_flight_"):
        flight_type = choice.split('_')[2]
        await handle_search_flight_request(query, flight_type, user_id)

    elif choice.startswith("flight_search_"):
        parts = choice.split('_')
        if len(parts) >= 4:
            flight_code = parts[2]
            date_str = parts[3]
            flight_type = context.user_data.get('flight_type', 'D')
            await handle_flight_search_result(query, flight_code, date_str, user_id, flight_type)

    elif choice == "dont_monitor":
        await query.edit_message_text(
            "✅ Alright! You can search for other flights or use /start to begin again."
        )

    elif choice == "stop_monitoring":
        await handle_stop_monitoring_button(query, user_id)

    elif choice == "back_to_menu":
        await handle_back_to_menu(query, context)

async def handle_back_to_menu(query, context):
    """Handle back to menu button for callback queries"""
    user_id = query.from_user.id
    if is_user_monitoring(user_id):
        await query.edit_message_text(
            "⚠️ You are currently monitoring a flight. Please stop monitoring first using /stop_monitor before using other commands."
        )
        return

    welcome_message = """
🛫 *Hello Passenger, Welcome to Flight Info Bot!*

I can help you find flight schedule information in real-time 😉

*Please select the type of flights you want to monitor:*
    """
    keyboard = [
        [
            InlineKeyboardButton("International", callback_data='I'),
            InlineKeyboardButton("Domestic", callback_data='D')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(welcome_message, reply_markup=reply_markup)

async def handle_stop_monitoring_button(query, user_id):
    """Handle stop monitoring button for callback queries"""
    global should_exit
    if user_id in monitored_flights:
        flight_no = monitored_flights[user_id].get('flight_no', 'Unknown')
        del monitored_flights[user_id]
        logger.info(f"User {user_id} stopped monitoring flight {flight_no} via button")

        if not monitored_flights:
            should_exit = True
            logger.info("No more users monitoring flights. Setting exit flag to True.")

        await query.edit_message_text(
            f"🚫 You have stopped monitoring flight {flight_no}.\n\n"
            "🔄 Program will now exit completely. Please restart with /start to begin again."
        )
    else:
        await query.edit_message_text(
            "❌ You are not currently monitoring any flights."
        )

async def handle_schedule_request(query, flight_type, date_str, user_id):
    """Handle schedule button clicks"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        flights = flight_bot.get_flights_by_date(date_str)
        filtered_flights = []
        for flight in flights:
            if flight['departure'] == flight_type:
                filtered_flights.append(flight)
        filtered_flights = filtered_flights[:20]
        if filtered_flights:
            message = f"📅 Flight Schedules {date_obj.strftime('%d %B %Y')}\n\n"
            for i, flight in enumerate(filtered_flights, 1):
                message += f"{i}. {flight['flightno']}\n"
                message += f"   📍 {flight['fromtolocation']}\n"
                message += f"   🕐 {flight['schedule']}\n\n"

            keyboard = [
                [InlineKeyboardButton("🔍 Search Specific Flight", callback_data=f"search_flight_{flight_type}")],
                [InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(message, reply_markup=reply_markup)
        else:
            keyboard = [
                [InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f"❌ No {flight_type} flights found on {date_str}.\n\n"
                "Please check the flight type or try again later.",
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Error in handle_schedule_request: {e}")
        await query.edit_message_text("❌ Error loading flight schedules. Please try again.")

async def handle_search_flight_request(query, flight_type, user_id):
    """Handle search flight button clicks"""
    keyboard = [
        [InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"🔍 Search for a Specific Flight\n\n"
        f"Please enter the flight code in this format:\n"
        f"`/flight [FLIGHT_CODE]`\n\n"
        f"Note: The system will automatically search for today's flights.\n"
        f"Make sure you've selected {flight_type} flight type.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_flight_search_result(query, flight_code, date_str, user_id, flight_type):
    """Handle flight search result button clicks"""
    try:
        flight_info = flight_bot.get_flight_info(flight_code, date_str)
        if flight_info:
            status_emoji = {
                'On Time': '✅',
                'Delayed': '⏰',
                'Cancelled': '❌',
                'Departed': '🛫',
                'Arrived': '🛬'
            }

            message = f"""
✈️ Flight Information {flight_info['flightno']}

📅 Schedule: {flight_info['schedule']}
⏰ Estimate: {flight_info['estimate']}

🚪 Gate: {flight_info['gatenumber']}
📦 Status: {status_emoji.get(flight_info['flightstat'], '')} {flight_info['flightstat']}
📍 Route: {flight_info['fromtolocation']}
            """

            logger.info(f"Creating monitoring button for flight: {flight_info.get('flightno')} with ID: {flight_info.get('id')}")
            keyboard = [
                [
                    InlineKeyboardButton("Start Monitoring 🔔", callback_data=f"monitor_{flight_info.get('id', 'unknown')}"),
                    InlineKeyboardButton("Don't Monitor", callback_data="dont_monitor")
                ],
                [InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(message, reply_markup=reply_markup)
        else:
            keyboard = [
                [InlineKeyboardButton("🔍 Search Again", callback_data=f"search_flight_{flight_type}")],
                [InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f"❌ Flight {flight_code} not found for today ({date_str}).",
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Error in handle_flight_search_result: {e}")
        await query.edit_message_text("❌ Error loading flight information. Please try again.")

async def flight_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_user_monitoring(user_id):
        await update.message.reply_text(
            "⚠️ You are currently monitoring a flight. Please stop monitoring first using /stop_monitor before searching for other flights."
        )
        return
    flight_type = context.user_data.get('flight_type', None)
    if flight_type is None:
        await update.message.reply_text(
            "❌ You need to select a flight type first! Please choose from Domestic or International by typing /start."
        )
        return

    if len(context.args) != 1:
        await update.message.reply_text(
            "❌ Incorrect format!\n\n"
            "Use: /flight [Flight_Code]"
        )
        return

    flight_code = context.args[0].upper()
    date_str = datetime.now().strftime('%Y-%m-%d')

    flight_info = flight_bot.get_flight_info(flight_code, date_str)

    if flight_info:
        if (flight_type == 'D' and not flight_info['departure'].startswith('I')) or (flight_type == 'I' and flight_info['departure'].startswith('I')):
            status_emoji = {
                'On Time': '✅',
                'Delayed': '⏰',
                'Cancelled': '❌',
                'Departed': '🛫',
                'Arrived': '🛬'
            }

            message = f"""
            ✈️ Flight Information {flight_info['flightno']}

            📅 Schedule: {flight_info['schedule']}
            ⏰ Estimate: {flight_info['estimate']}

            🚪 Gate: {flight_info['gatenumber']}
            📦 Status: {status_emoji.get(flight_info['flightstat'], '')} {flight_info['flightstat']}
            📍 Route: {flight_info['fromtolocation']}
            """
            await update.message.reply_text(message)

            logger.info(f"Creating monitoring button for flight: {flight_info.get('flightno')} with ID: {flight_info.get('id')}")
            keyboard = [
                [
                    InlineKeyboardButton("Start Monitoring 🔔", callback_data=f"monitor_{flight_info.get('id', 'unknown')}"),
                    InlineKeyboardButton("Don't Monitor", callback_data="dont_monitor")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "Would you like to monitor the status of this flight? You will receive updates if the status changes 😉\n\n",
                reply_markup=reply_markup
            )
        else:
            flight_type_name = "Domestic" if flight_info['departure'].startswith ('D') else "International"
            actual_type = "International" if flight_info['departure'].startswith('I') else "Domestic"
            await update.message.reply_text(
                f"❌ Flight {flight_code} is a {actual_type} flight, but you selected {flight_type_name} flights.\n\n"
                "Please use /start command again and choose the correct flight type."
            )
            return
    else:
        await update.message.reply_text(
            f"❌ Flight {flight_code} not found for today ({date_str})."
        )

async def schedule_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_user_monitoring(user_id):
        await update.message.reply_text(
            "⚠️ You are currently monitoring a flight. Please stop monitoring first using /stop_monitor before viewing schedules."
        )
        return
    if len(context.args) != 1:
        await update.message.reply_text(
            "❌ Incorrect format!\n\n"
            "Use: /schedule [date]"
        )
        return

    flight_type = context.user_data.get('flight_type', None)
    if flight_type is None:
        await update.message.reply_text(
            "❌ You need to select a flight type first! Please choose from Domestic or International by typing /start."
        )
        return

    date_str = context.args[0]
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        await update.message.reply_text(
            "❌ Incorrect date format!\n\n"
            "Use format: YYYY-MM-DD"
        )
        return

    await update.message.reply_text("🔍 Searching for Flight Schedules...")
    flights = flight_bot.get_flights_by_date(date_str)

    filtered_flights = []

    for flight in flights:
        if flight['departure'] == flight_type:
            filtered_flights.append(flight)
    filtered_flights = filtered_flights[:20]

    if filtered_flights:
        message = f"📅 Flight Schedules {date_obj.strftime('%d %B %Y')}\n\n"
        for i, flight in enumerate(filtered_flights, 1):
            message += f"{i}. *{flight['flightno']}*\n"
            message += f"   📍 {flight['fromtolocation']}\n"
            message += f"   🕐 {flight['schedule']}\n\n"
        await update.message.reply_text(message)
    else:
        await update.message.reply_text(
            f"❌ No flights of type {flight_type} on {date_str}."
        )

async def stop_monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in monitored_flights:
        flight_no = monitored_flights[user_id].get('flight_no', 'Unknown')
        del monitored_flights[user_id]
        logger.info(f"User {user_id} manually stopped monitoring flight {flight_no}")
        await update.message.reply_text(
            f"🚫 You have stopped monitoring flight {flight_no}.\n\n"
            "✅ You can now use all bot commands again. Type /start to begin."
        )
    else:
        await update.message.reply_text(
            "❌ You are not currently monitoring any flights."
        )

async def debug_monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Debug command to check monitoring status"""
    user_id = update.effective_user.id

    debug_message = "🔍 Debug Information\n\n"
    debug_message += f"Your User ID: `{user_id}`\n"
    debug_message += f"Total Monitored Flights: {len(monitored_flights)}\n\n"

    if user_id in monitored_flights:
        flight_data = monitored_flights[user_id]
        debug_message += "✅ *You are monitoring:*\n"
        debug_message += f"Flight: {flight_data['flight_no']}\n"
        debug_message += f"Flight ID: {flight_data['flight_id']}\n"
        debug_message += f"Last Status: {flight_data['last_status']}\n"
        debug_message += f"Last Schedule: {flight_data['last_schedule']}\n"
        debug_message += f"Last Estimate: {flight_data['last_estimate']}\n"
        debug_message += f"Notifications Sent: {flight_data.get('notification_count', 0)}\n"
        debug_message += f"Checks Performed: {flight_data.get('check_count', 0)}\n"
        debug_message += f"Last Seen: {flight_data.get('last_seen', 'N/A')}\n\n"
        try:
            current_flight = flight_bot.get_flight_info_by_id(flight_data['flight_id'])
            if current_flight:
                debug_message += "✅ Live API Check: SUCCESS\n"
                debug_message += f"Current Status: {current_flight['flightstat']}\n"
                debug_message += f"Current Schedule: {current_flight['schedule']}\n"
                debug_message += f"Current Estimate: {current_flight['estimate']}\n"
            else:
                debug_message += "❌ Live API Check: FLIGHT NOT FOUND\n"
        except Exception as e:
            debug_message += f"❌ Live API Check: ERROR - {str(e)}*\n"
    else:
        debug_message += "❌ You are not monitoring any flights\n"

    debug_message += f"\nAll Monitored Users: {list(monitored_flights.keys())}"

    await update.message.reply_text(debug_message)

async def test_notification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test notification sending"""
    user_id = update.effective_user.id

    try:
        await update.message.reply_text(
            "🧪 Test Notification\n\n"
            "✅ Bot can send messages successfully!\n"
            f"Your User ID: {user_id}\n"
            f"Message sent at: {datetime.now().strftime('%H:%M:%S')}"
        )
        logger.info(f"Test notification sent successfully to user {user_id}")
    except Exception as e:
        logger.error(f"Failed to send test notification to user {user_id}: {e}")
        await update.message.reply_text(
            f"❌ Failed to send notification: {str(e)}"
        )

def normalize_value(value):
    if value is None:
        return None
    try:
        return str(value).strip()
    except Exception:
        return str(value)


def safe_string_compare(val1, val2):
    """Safely compare two values as trimmed strings, handling None values"""
    str1 = normalize_value(val1)
    str2 = normalize_value(val2)
    return str1 == str2


def normalize_status(value):
    v = normalize_value(value)
    return v.lower() if isinstance(v, str) else v

def format_flight_status_message(flight_data, changes=None):
    """Format flight status message with current data"""
    status_emoji = {
        'On Time': '✅',
        'Delayed': '⏰',
        'Cancelled': '❌',
        'Departed': '🛫',
        'Arrived': '🛬',
        'Gate Close': '🚪',
        'Boarding': '🎫',
        'Check-in': '📋'
    }

    message = f"✈️ Flight {flight_data['flightno']} Status*\n\n"
    message += f"🏢 Operator: {flight_data['operator']}\n"
    message += f"📅 Schedule: {flight_data['schedule']}\n"
    message += f"⏰ Estimate: {flight_data['estimate']}\n"
    message += f"🚪 Gate: {flight_data['gatenumber']}\n"
    message += f"📦 Status: {status_emoji.get(flight_data['flightstat'], '📊')} {flight_data['flightstat']}\n"
    message += f"📍 Route: {flight_data['fromtolocation']}\n"


    if changes:
        message += f"\n🔄 *Recent Changes:*\n"
        for change in changes:
            message += f"• {change}\n"

    message += f"\n🕐 *Last Updated:* {datetime.now().strftime('%H:%M:%S')}"

    return message

async def monitor_flight_status(application=None):
    """Enhanced real-time monitoring system with proper change detection"""
    global should_exit
    logger.info("🔄 Starting enhanced flight monitoring system...")

    while not should_exit:
        try:
            if not monitored_flights:
                await asyncio.sleep(MONITOR_INTERVAL_SECONDS)
                continue

            users_to_remove = []

            logger.info(f"Monitoring {len(monitored_flights)} flights: {list(monitored_flights.keys())}")

            for user_id, monitoring_data in list(monitored_flights.items()):
                try:
                    flight_id = monitoring_data['flight_id']

                    check_count = monitoring_data.get('check_count', 0) + 1
                    monitored_flights[user_id]['check_count'] = check_count

                    current_flight = flight_bot.get_flight_info_by_id(flight_id)

                    if current_flight is None:
                        logger.warning(f"Flight ID {flight_id} currently unavailable from API for user {user_id}")

                        bot = application.bot if application and hasattr(application, 'bot') else None
                        if bot and not monitoring_data.get('missing_notified'):
                            try:
                                last_message_id = monitoring_data.get('last_message_id')
                                if last_message_id:
                                    try:
                                        await bot.delete_message(chat_id=user_id, message_id=last_message_id)
                                        logger.info(f"Deleted previous notification message {last_message_id} for user {user_id} before unavailable notification")
                                    except Exception as delete_error:
                                        logger.warning(f"Could not delete previous message {last_message_id} for user {user_id}: {delete_error}")

                                sent_message = await bot.send_message(
                                    chat_id=user_id,
                                    text=(
                                        f"⚠️ Flight {monitoring_data['flight_no']} (ID: {flight_id}) is temporarily unavailable from the API.\n\n"
                                        f"📊 Last known status: {monitoring_data['last_status']}\n"
                                        f"⏰ Last schedule: {monitoring_data['last_schedule']}\n"
                                        f"🕐 Last estimate: {monitoring_data['last_estimate']}\n\n"
                                        f"🔁 Monitoring will continue and retry automatically."
                                    ),
                                    parse_mode='Markdown'
                                )
                                monitored_flights[user_id]['last_message_id'] = sent_message.message_id
                                monitored_flights[user_id]['missing_notified'] = True
                                logger.info(f"Sent temporary unavailable notification to user {user_id}")
                            except Exception as e:
                                logger.error(f"Failed to send temporary unavailable notification to user {user_id}: {e}")
                        continue

                    changes = []
                    status_changed = False

                    current_status = normalize_status(current_flight.get('flightstat'))
                    current_schedule = normalize_value(current_flight.get('schedule'))
                    current_estimate = normalize_value(current_flight.get('estimate'))
                    current_gate = normalize_value(current_flight.get('gatenumber'))

                    stored_status = normalize_status(monitoring_data['last_status'])
                    stored_schedule = normalize_value(monitoring_data['last_schedule'])
                    stored_estimate = normalize_value(monitoring_data['last_estimate'])
                    stored_gate = normalize_value(monitoring_data.get('last_gate'))

                    logger.info(f"Flight {current_flight['flightno']} comparison (check #{check_count}):")
                    logger.info(f"  Status: '{stored_status}' vs '{current_status}' - {'CHANGED' if stored_status != current_status else 'SAME'}")
                    logger.info(f"  Schedule: '{stored_schedule}' vs '{current_schedule}' - {'CHANGED' if stored_schedule != current_schedule else 'SAME'}")
                    logger.info(f"  Estimate: '{stored_estimate}' vs '{current_estimate}' - {'CHANGED' if stored_estimate != current_estimate else 'SAME'}")
                    logger.info(f"  Gate: '{stored_gate}' vs '{current_gate}' - {'CHANGED' if stored_gate != current_gate else 'SAME'}")

                    if stored_status != current_status:
                        changes.append(f"Status: {monitoring_data['last_status']} → {current_flight.get('flightstat')}")
                        status_changed = True
                        logger.info(f"STATUS CHANGE DETECTED for flight {current_flight['flightno']}: '{stored_status}' → '{current_status}'")

                    if not safe_string_compare(stored_schedule, current_schedule):
                        changes.append(f"Schedule: {stored_schedule} → {current_schedule}")
                        status_changed = True
                        logger.info(f"SCHEDULE CHANGE DETECTED for flight {current_flight['flightno']}: '{stored_schedule}' → '{current_schedule}'")

                    if not safe_string_compare(stored_estimate, current_estimate):
                        changes.append(f"Estimate: {stored_estimate} → {current_estimate}")
                        status_changed = True
                        logger.info(f"ESTIMATE CHANGE DETECTED for flight {current_flight['flightno']}: '{stored_estimate}' → '{current_estimate}'")

                    if not safe_string_compare(stored_gate, current_gate):
                        changes.append(f"Gate: {stored_gate or 'N/A'} → {current_gate or 'N/A'}")
                        status_changed = True
                        logger.info(f"GATE CHANGE DETECTED for flight {current_flight['flightno']}: '{stored_gate}' → '{current_gate}'")

                    bot = application.bot if application and hasattr(application, 'bot') else None

                    if bot and status_changed:
                        try:
                            last_message_id = monitoring_data.get('last_message_id')
                            if last_message_id:
                                try:
                                    await bot.delete_message(chat_id=user_id, message_id=last_message_id)
                                    logger.info(f"Deleted previous notification message {last_message_id} for user {user_id}")
                                except Exception as delete_error:
                                    logger.warning(f"Could not delete previous message {last_message_id} for user {user_id}: {delete_error}")

                            notification_message = f"🚨 Flight Update Alert!\n\n"
                            notification_message += format_flight_status_message(current_flight, changes)

                            keyboard = [
                                [InlineKeyboardButton("🚫 Stop Monitoring", callback_data="stop_monitoring")]
                            ]
                            reply_markup = InlineKeyboardMarkup(keyboard)

                            sent_message = await bot.send_message(
                                chat_id=user_id,
                                text=notification_message,
                                reply_markup=reply_markup
                            )

                            new_message_id = sent_message.message_id

                            logger.info(f"Sent update notification to user {user_id} for flight {current_flight['flightno']} - Changes: {changes}")

                            monitored_flights[user_id].update({
                                'last_status': current_status,
                                'last_schedule': current_schedule,
                                'last_estimate': current_estimate,
                                'last_gate': current_gate,
                                'last_seen': datetime.now(),
                                'notification_count': monitoring_data.get('notification_count', 0) + 1,
                                'last_message_id': new_message_id
                            })

                        except Exception as e:
                            logger.error(f"Failed to send update notification to user {user_id}: {e}")
                    else:
                        monitored_flights[user_id]['last_seen'] = datetime.now()

                    final_statuses = ['Gate Close']
                    if current_status in final_statuses:
                        if bot and not monitoring_data.get('final_notified'):
                            try:
                                last_message_id = monitoring_data.get('last_message_id')
                                if last_message_id:
                                    try:
                                        await bot.delete_message(chat_id=user_id, message_id=last_message_id)
                                        logger.info(f"Deleted previous notification message {last_message_id} for user {user_id} before final status")
                                    except Exception as delete_error:
                                        logger.warning(f"Could not delete previous message {last_message_id} for user {user_id}: {delete_error}")

                                final_message = f"🏁 Flight {current_flight['flightno']} - Final Status\n\n"
                                final_message += format_flight_status_message(current_flight)
                                final_message += (
                                    f"\n\n✅ Flight has reached final status ({current_status}). Monitoring has been automatically stopped.\n"
                                    f"🔄 Program will now exit completely. Please restart with /start to begin again."
                                )
                                keyboard = [
                                    [InlineKeyboardButton("🚫 Stop Monitoring", callback_data="stop_monitoring")]
                                ]
                                reply_markup = InlineKeyboardMarkup(keyboard)
                                await bot.send_message(
                                    chat_id=user_id,
                                    text=final_message,
                                    reply_markup=reply_markup
                                )
                                monitored_flights[user_id]['final_notified'] = True
                                logger.info(f"Sent final status notification to user {user_id}")
                            except Exception as e:
                                logger.error(f"Failed to send final status to user {user_id}: {e}")
                        users_to_remove.append(user_id)
                        logger.info(f"Auto-stopping monitoring for user {user_id} - flight reached final status: {current_status}")

                except Exception as e:
                    logger.error(f"Error processing monitored flight for user {user_id}: {e}")
                    logger.error(traceback.format_exc())
                    continue

            for user_id in users_to_remove:
                if user_id in monitored_flights:
                    del monitored_flights[user_id]
                    logger.info(f"Removed user {user_id} from monitoring list")

            if not monitored_flights and users_to_remove:
                should_exit = True
                logger.info("All users removed from monitoring. Setting exit flag to True.")

        except Exception as e:
            logger.error(f"Error in monitor_flight_status main loop: {e}")
            logger.error(traceback.format_exc())

        await asyncio.sleep(MONITOR_INTERVAL_SECONDS)

    logger.info("🛑 Monitoring loop exiting due to exit flag being set.")