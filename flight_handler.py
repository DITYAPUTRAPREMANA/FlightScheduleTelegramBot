from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from flight_bot import FlightScheduleBot
import asyncio
import logging
import traceback
from config import MONITOR_INTERVAL_SECONDS
from language import get_text, get_status_emoji, get_month_names

logger = logging.getLogger(__name__)
flight_bot = FlightScheduleBot()

monitored_flights = {}
should_exit = False
user_message_history = {}

def is_user_monitoring(user_id):
    """Check if user is currently monitoring a flight"""
    return user_id in monitored_flights

async def auto_delete_previous_message(bot, user_id, chat_id=None):
    """Auto delete previous message to prevent message accumulation"""
    try:
        if user_id in user_message_history:
            message_id = user_message_history[user_id]
            if chat_id is None:
                chat_id = user_id
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
            logger.info(f"Auto-deleted previous message {message_id} for user {user_id}")
    except Exception as e:
        logger.warning(f"Could not auto-delete previous message for user {user_id}: {e}")

def store_message_id(user_id, message_id):
    """Store message ID for auto-delete functionality"""
    user_message_history[user_id] = message_id

async def safe_edit_message(query, text, reply_markup=None, parse_mode=None):
    """Safely edit message with error handling"""
    try:
        return await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
    except Exception as e:
        logger.warning(f"Could not edit message, sending new message instead: {e}")
        user_id = query.from_user.id
        await auto_delete_previous_message(query.get_bot(), user_id, query.message.chat_id)
        return await query.get_bot().send_message(
            chat_id=query.message.chat_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    await auto_delete_previous_message(update.get_bot(), user_id)

    if is_user_monitoring(user_id):
        user_language = context.user_data.get('language', 'en')
        sent_message = await update.message.reply_text(
            get_text('currently_monitoring', user_language)
        )
        store_message_id(user_id, sent_message.message_id)
        return

    user_language = context.user_data.get('language')
    if user_language is None:
        welcome_message = f"""
{get_text('welcome_title', 'en')}

{get_text('welcome_subtitle', 'en')}

{get_text('select_language', 'en')}
        """
        keyboard = [
            [
                InlineKeyboardButton("🇺🇸 English", callback_data='lang_en'),
                InlineKeyboardButton("🇮🇩 Bahasa Indonesia", callback_data='lang_id')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        sent_message = await update.message.reply_text(welcome_message, reply_markup=reply_markup)
        store_message_id(user_id, sent_message.message_id)
    else:
        await show_flight_type_selection(update, context, user_language)

async def show_flight_type_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, language: str):
    """Show flight type selection menu in user's language"""
    user_id = update.effective_user.id if hasattr(update, 'effective_user') else update.from_user.id

    welcome_message = f"""
{get_text('welcome_title', language)}

{get_text('welcome_subtitle', language)}

{get_text('select_flight_type', language)}
    """
    keyboard = [
        [
            InlineKeyboardButton(get_text('international', language), callback_data='I'),
            InlineKeyboardButton(get_text('domestic', language), callback_data='D')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if hasattr(update, 'message'):
        await auto_delete_previous_message(update.get_bot(), user_id)
        sent_message = await update.message.reply_text(welcome_message, reply_markup=reply_markup)
        store_message_id(user_id, sent_message.message_id)
    else:
        sent_message = await update.edit_message_text(welcome_message, reply_markup=reply_markup)
        store_message_id(user_id, sent_message.message_id)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    choice = query.data
    user_id = query.from_user.id

    await query.answer()

    if choice.startswith('lang_'):
        language = choice.split('_')[1]
        was_changing_language = context.user_data.get('language') is not None
        context.user_data['language'] = language
        if was_changing_language:
            language_name = "English" if language == 'en' else "Bahasa Indonesia"
            confirmation_message = f"✅ {get_text('language_changed', language, language_name=language_name)}\n\n"
            confirmation_message += f"{get_text('welcome_title', language)}\n\n"
            confirmation_message += f"{get_text('welcome_subtitle', language)}\n\n"
            confirmation_message += f"{get_text('select_flight_type', language)}"
            keyboard = [
                [
                    InlineKeyboardButton(get_text('international', language), callback_data='I'),
                    InlineKeyboardButton(get_text('domestic', language), callback_data='D')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            sent_message = await safe_edit_message(query, confirmation_message, reply_markup=reply_markup)
            store_message_id(user_id, sent_message.message_id)
        else:
            await show_flight_type_selection(query, context, language)
        return

    user_language = context.user_data.get('language', 'en')
    if is_user_monitoring(user_id) and not choice.startswith("stop_monitor_"):
        sent_message = await safe_edit_message(query, get_text('currently_monitoring', user_language))
        store_message_id(user_id, sent_message.message_id)
        return
    if choice in ['I', 'D']:
        context.user_data['flight_type'] = choice
        flight_type_name = get_text('international', user_language) if choice == 'I' else get_text('domestic', user_language)

        from datetime import timedelta
        today = datetime.now()
        keyboard = [
            [
                InlineKeyboardButton(get_text('schedule', user_language), callback_data=f"schedule_{choice}_{today.strftime('%Y-%m-%d')}"),
                InlineKeyboardButton(get_text('search_flight', user_language), callback_data=f"search_flight_{choice}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        sent_message = await safe_edit_message(
            query,
            text=f"{get_text('flight_selected', user_language, flight_type=flight_type_name.lower())}\n\n"
                 f"{get_text('what_would_you_like', user_language)}\n\n"
                 f"{get_text('view_schedules', user_language)}\n"
                 f"{get_text('search_specific', user_language)}",
            reply_markup=reply_markup
        )
        store_message_id(user_id, sent_message.message_id)

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
                'last_message_id': None,
                'language': user_language
            }

            logger.info(f"User {user_id} started monitoring flight {flight_info['flightno']} (ID: {flight_id})")
            logger.info(f"Initial monitoring data: {monitored_flights[user_id]}")

            keyboard = [
                [InlineKeyboardButton(get_text('stop_monitoring', user_language), callback_data=f"stop_monitor_{flight_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            sent_message = await safe_edit_message(
                query,
                f"{get_text('monitoring_started', user_language, flight_no=flight_info['flightno'])}\n\n"
                f"{get_text('current_status', user_language)} {flight_info['flightstat']}\n"
                f"{get_text('schedule_label', user_language)} {flight_info['schedule']}\n"
                f"{get_text('estimate_label', user_language)} {flight_info['estimate']}\n"
                f"{get_text('gate_label', user_language)} {flight_info['gatenumber']}\n\n"
                f"{get_text('monitoring_notifications', user_language)}\n\n"
                f"{get_text('monitoring_interval', user_language)}",
                reply_markup=reply_markup
            )
            if sent_message:
                monitored_flights[user_id]['last_message_id'] = sent_message.message_id
                store_message_id(user_id, sent_message.message_id)

    elif choice.startswith("stop_monitor_"):
        flight_id = choice.split('_')[-1]
        if user_id in monitored_flights:
            flight_no = monitored_flights[user_id].get('flight_no', flight_id)
            user_lang = monitored_flights[user_id].get('language', 'en')
            del monitored_flights[user_id]
            logger.info(f"User {user_id} stopped monitoring flight {flight_no}")
            sent_message = await safe_edit_message(
                query,
                f"{get_text('monitoring_stopped', user_lang, flight_no=flight_no)}\n\n"
                f"{get_text('can_use_commands', user_lang)}"
            )
            store_message_id(user_id, sent_message.message_id)
        else:
            sent_message = await safe_edit_message(query, get_text('no_active_monitoring', user_language))
            store_message_id(user_id, sent_message.message_id)

    elif choice.startswith("schedule_"):
        parts = choice.split('_')
        if len(parts) >= 3:
            flight_type = parts[1]
            date_str = parts[2]
            await handle_schedule_request(query, flight_type, date_str, user_id, context)

    elif choice.startswith("search_flight_"):
        flight_type = choice.split('_')[2]
        await handle_search_flight_request(query, flight_type, user_id, context)

    elif choice.startswith("flight_search_"):
        parts = choice.split('_')
        if len(parts) >= 4:
            flight_code = parts[2]
            date_str = parts[3]
            flight_type = context.user_data.get('flight_type', 'D')
            await handle_flight_search_result(query, flight_code, date_str, user_id, flight_type, context)

    elif choice == "dont_monitor":
        sent_message = await safe_edit_message(
            query,
            f"✅ {get_text('can_use_commands', user_language)}"
        )
        store_message_id(user_id, sent_message.message_id)

    elif choice == "back_to_menu":
        await handle_back_to_menu(query, context)

async def handle_back_to_menu(query, context):
    """Handle back to menu button for callback queries"""
    user_id = query.from_user.id
    user_language = context.user_data.get('language', 'en')
    if is_user_monitoring(user_id):
        await query.edit_message_text(
            get_text('currently_monitoring', user_language)
        )
        return

    await show_flight_type_selection(query, context, user_language)

async def handle_schedule_request(query, flight_type, date_str, user_id, context):
    """Handle schedule button clicks"""
    try:
        user_language = context.user_data.get('language', 'en')
        if user_id in monitored_flights:
            user_language = monitored_flights[user_id].get('language', user_language)
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        flights = flight_bot.get_flights_by_date(date_str)
        filtered_flights = []
        for flight in flights:
            if flight['departure'] == flight_type:
                filtered_flights.append(flight)
        filtered_flights = filtered_flights[:20]
        if filtered_flights:
            if user_language == 'id':
                month_names = get_month_names('id')
                date_formatted = date_obj.strftime('%d %B %Y')
                for eng_month, ind_month in month_names.items():
                    date_formatted = date_formatted.replace(eng_month, ind_month)
            else:
                date_formatted = date_obj.strftime('%d %B %Y')
            message = f"{get_text('flight_schedules', user_language, date=date_formatted)}\n\n"
            for i, flight in enumerate(filtered_flights, 1):
                message += f"{i}. {flight['flightno']}\n"
                message += f"   📍 {flight['fromtolocation']}\n"
                message += f"   🕐 {flight['schedule']}\n\n"

            keyboard = [
                [InlineKeyboardButton(get_text('search_specific_flight', user_language), callback_data=f"search_flight_{flight_type}")],
                [InlineKeyboardButton(get_text('back_to_menu', user_language), callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            sent_message = await safe_edit_message(query, message, reply_markup=reply_markup)
            store_message_id(user_id, sent_message.message_id)
        else:
            keyboard = [
                [InlineKeyboardButton(get_text('back_to_menu', user_language), callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            sent_message = await safe_edit_message(
                query,
                f"{get_text('no_flights_found', user_language, flight_type=flight_type, date=date_str)}\n\n"
                f"{get_text('check_flight_type', user_language)}",
                reply_markup=reply_markup
            )
            store_message_id(user_id, sent_message.message_id)
    except Exception as e:
        logger.error(f"Error in handle_schedule_request: {e}")
        sent_message = await safe_edit_message(query, get_text('error_loading_schedules', user_language))
        store_message_id(user_id, sent_message.message_id)

async def handle_search_flight_request(query, flight_type, user_id, context):
    """Handle search flight button clicks"""
    user_language = context.user_data.get('language', 'en')
    if user_id in monitored_flights:
        user_language = monitored_flights[user_id].get('language', user_language)
    keyboard = [
        [InlineKeyboardButton(get_text('back_to_menu', user_language), callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    sent_message = await safe_edit_message(
        query,
        f"{get_text('search_specific_flight', user_language)}\n\n"
        f"{get_text('enter_flight_code', user_language)}\n"
        f"{get_text('flight_command_format', user_language)}\n\n"
        f"{get_text('search_note', user_language)}\n"
        f"{get_text('make_sure_selected', user_language, flight_type=flight_type)}",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    store_message_id(user_id, sent_message.message_id)

async def handle_flight_search_result(query, flight_code, date_str, user_id, flight_type, context):
    """Handle flight search result button clicks"""
    try:
        user_language = context.user_data.get('language', 'en')
        if user_id in monitored_flights:
            user_language = monitored_flights[user_id].get('language', user_language)
        flight_info = flight_bot.get_flight_info(flight_code, date_str)
        if flight_info:
            status_emoji = get_status_emoji(flight_info['flightstat'])

            message = f"""
{get_text('flight_info_title', user_language, flight_no=flight_info['flightno'])}

{get_text('schedule_label', user_language)} {flight_info['schedule']}
{get_text('estimate_label', user_language)} {flight_info['estimate']}

{get_text('gate_label', user_language)} {flight_info['gatenumber']}
{get_text('status_label', user_language)} {status_emoji} {flight_info['flightstat']}
{get_text('route_label', user_language)} {flight_info['fromtolocation']}
            """

            logger.info(f"Creating monitoring button for flight: {flight_info.get('flightno')} with ID: {flight_info.get('id')}")
            keyboard = [
                [
                    InlineKeyboardButton(get_text('start_monitoring', user_language), callback_data=f"monitor_{flight_info.get('id', 'unknown')}"),
                    InlineKeyboardButton(get_text('dont_monitor', user_language), callback_data="dont_monitor")
                ],
                [InlineKeyboardButton(get_text('back_to_menu', user_language), callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            sent_message = await safe_edit_message(query, message, reply_markup=reply_markup)
            store_message_id(user_id, sent_message.message_id)
        else:
            keyboard = [
                [InlineKeyboardButton(get_text('search_again', user_language), callback_data=f"search_flight_{flight_type}")],
                [InlineKeyboardButton(get_text('back_to_menu', user_language), callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            sent_message = await safe_edit_message(
                query,
                get_text('flight_not_found', user_language, flight_code=flight_code, date=date_str),
                reply_markup=reply_markup
            )
            store_message_id(user_id, sent_message.message_id)
    except Exception as e:
        logger.error(f"Error in handle_flight_search_result: {e}")
        sent_message = await safe_edit_message(query, get_text('error_loading_flight_info', user_language))
        store_message_id(user_id, sent_message.message_id)

async def flight_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_language = context.user_data.get('language', 'en')
    if is_user_monitoring(user_id):
        await update.message.reply_text(
            get_text('currently_monitoring', user_language)
        )
        return
    flight_type = context.user_data.get('flight_type', None)
    if flight_type is None:
        await update.message.reply_text(
            get_text('select_flight_type_first', user_language)
        )
        return

    if len(context.args) != 1:
        await update.message.reply_text(
            f"{get_text('incorrect_format', user_language)}\n\n"
            f"{get_text('use_flight_format', user_language)}"
        )
        return

    flight_code = context.args[0].upper()
    date_str = datetime.now().strftime('%Y-%m-%d')

    flight_info = flight_bot.get_flight_info(flight_code, date_str)

    if flight_info:
        if (flight_type == 'D' and not flight_info['departure'].startswith('I')) or (flight_type == 'I' and flight_info['departure'].startswith('I')):
            status_emoji = get_status_emoji(flight_info['flightstat'])

            message = f"""
{get_text('flight_info_title', user_language, flight_no=flight_info['flightno'])}

{get_text('schedule_label', user_language)} {flight_info['schedule']}
{get_text('estimate_label', user_language)} {flight_info['estimate']}

{get_text('gate_label', user_language)} {flight_info['gatenumber']}
{get_text('status_label', user_language)} {status_emoji} {flight_info['flightstat']}
{get_text('route_label', user_language)} {flight_info['fromtolocation']}
            """
            await update.message.reply_text(message)

            logger.info(f"Creating monitoring button for flight: {flight_info.get('flightno')} with ID: {flight_info.get('id')}")
            keyboard = [
                [
                    InlineKeyboardButton(get_text('start_monitoring', user_language), callback_data=f"monitor_{flight_info.get('id', 'unknown')}"),
                    InlineKeyboardButton(get_text('dont_monitor', user_language), callback_data="dont_monitor")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"{get_text('would_you_like_monitor', user_language)}\n\n",
                reply_markup=reply_markup
            )
        else:
            flight_type_name = get_text('domestic', user_language) if flight_info['departure'].startswith ('D') else get_text('international', user_language)
            actual_type = get_text('international', user_language) if flight_info['departure'].startswith('I') else get_text('domestic', user_language)
            await update.message.reply_text(
                f"❌ Flight {flight_code} is a {actual_type} flight, but you selected {flight_type_name} flights.\n\n"
                f"{get_text('select_flight_type_first', user_language)}"
            )
            return
    else:
        await update.message.reply_text(
            get_text('flight_not_found', user_language, flight_code=flight_code, date=date_str)
        )

async def schedule_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_language = context.user_data.get('language', 'en')
    if is_user_monitoring(user_id):
        await update.message.reply_text(
            get_text('currently_monitoring', user_language)
        )
        return
    if len(context.args) != 1:
        await update.message.reply_text(
            f"{get_text('incorrect_format', user_language)}\n\n"
            f"Use: /schedule [date]"
        )
        return

    flight_type = context.user_data.get('flight_type', None)
    if flight_type is None:
        await update.message.reply_text(
            get_text('select_flight_type_first', user_language)
        )
        return

    date_str = context.args[0]
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        await update.message.reply_text(
            f"{get_text('incorrect_format', user_language)}\n\n"
            f"Use format: YYYY-MM-DD"
        )
        return

    await update.message.reply_text(get_text('searching_schedules', user_language))
    flights = flight_bot.get_flights_by_date(date_str)

    filtered_flights = []

    for flight in flights:
        if flight['departure'] == flight_type:
            filtered_flights.append(flight)
    filtered_flights = filtered_flights[:20]

    if filtered_flights:
        if user_language == 'id':
            month_names = get_month_names('id')
            date_formatted = date_obj.strftime('%d %B %Y')
            for eng_month, ind_month in month_names.items():
                date_formatted = date_formatted.replace(eng_month, ind_month)
        else:
            date_formatted = date_obj.strftime('%d %B %Y')
        message = f"{get_text('flight_schedules', user_language, date=date_formatted)}\n\n"
        for i, flight in enumerate(filtered_flights, 1):
            message += f"{i}. *{flight['flightno']}*\n"
            message += f"   📍 {flight['fromtolocation']}\n"
            message += f"   🕐 {flight['schedule']}\n\n"
        await update.message.reply_text(message)
    else:
        await update.message.reply_text(
            get_text('no_flights_type', user_language, flight_type=flight_type, date=date_str)
        )

async def stop_monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_language = context.user_data.get('language', 'en')
    if user_id in monitored_flights:
        flight_no = monitored_flights[user_id].get('flight_no', 'Unknown')
        del monitored_flights[user_id]
        logger.info(f"User {user_id} manually stopped monitoring flight {flight_no}")
        await update.message.reply_text(
            f"{get_text('monitoring_stopped', user_language, flight_no=flight_no)}\n\n"
            f"{get_text('can_use_commands', user_language)}"
        )
    else:
        await update.message.reply_text(
            get_text('not_monitoring_any', user_language)
        )

async def debug_monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Debug command to check monitoring status"""
    user_id = update.effective_user.id
    user_language = context.user_data.get('language', 'en')

    debug_message = f"{get_text('debug_info', user_language)}\n\n"
    debug_message += f"{get_text('your_user_id', user_language)} `{user_id}`\n"
    debug_message += f"{get_text('total_monitored', user_language)} {len(monitored_flights)}\n\n"

    if user_id in monitored_flights:
        flight_data = monitored_flights[user_id]
        debug_message += f"{get_text('you_are_monitoring', user_language)}\n"
        debug_message += f"Flight: {flight_data['flight_no']}\n"
        debug_message += f"{get_text('flight_id', user_language)} {flight_data['flight_id']}\n"
        debug_message += f"Last Status: {flight_data['last_status']}\n"
        debug_message += f"Last Schedule: {flight_data['last_schedule']}\n"
        debug_message += f"Last Estimate: {flight_data['last_estimate']}\n"
        debug_message += f"{get_text('notifications_sent', user_language)} {flight_data.get('notification_count', 0)}\n"
        debug_message += f"{get_text('checks_performed', user_language)} {flight_data.get('check_count', 0)}\n"
        debug_message += f"{get_text('last_seen', user_language)} {flight_data.get('last_seen', 'N/A')}\n\n"
        try:
            current_flight = flight_bot.get_flight_info_by_id(flight_data['flight_id'])
            if current_flight:
                debug_message += f"✅ {get_text('live_api_check', user_language)} {get_text('success', user_language)}\n"
                debug_message += f"Current Status: {current_flight['flightstat']}\n"
                debug_message += f"Current Schedule: {current_flight['schedule']}\n"
                debug_message += f"Current Estimate: {current_flight['estimate']}\n"
            else:
                debug_message += f"❌ {get_text('live_api_check', user_language)} {get_text('flight_not_found_debug', user_language)}\n"
        except Exception as e:
            debug_message += f"❌ {get_text('live_api_check', user_language)} {get_text('error', user_language)} - {str(e)}*\n"
    else:
        debug_message += f"{get_text('not_monitoring_debug', user_language)}\n"

    debug_message += f"\n{get_text('all_monitored_users', user_language)} {list(monitored_flights.keys())}"

    await update.message.reply_text(debug_message)

async def test_notification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test notification sending"""
    user_id = update.effective_user.id
    user_language = context.user_data.get('language', 'en')

    try:
        await update.message.reply_text(
            f"{get_text('test_notification', user_language)}\n\n"
            f"{get_text('bot_can_send', user_language)}\n"
            f"{get_text('your_user_id', user_language)} {user_id}\n"
            f"{get_text('message_sent_at', user_language)} {datetime.now().strftime('%H:%M:%S')}"
        )
        logger.info(f"Test notification sent successfully to user {user_id}")
    except Exception as e:
        logger.error(f"Failed to send test notification to user {user_id}: {e}")
        await update.message.reply_text(
            f"{get_text('failed_to_send', user_language)} {str(e)}"
        )

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Change user's language preference"""
    user_id = update.effective_user.id
    user_language = context.user_data.get('language', 'en')

    await auto_delete_previous_message(update.get_bot(), user_id)

    if is_user_monitoring(user_id):
        sent_message = await update.message.reply_text(
            get_text('currently_monitoring', user_language)
        )
        store_message_id(user_id, sent_message.message_id)
        return

    welcome_message = f"""
{get_text('welcome_title', user_language)}

{get_text('welcome_subtitle', user_language)}

{get_text('select_language', user_language)}
    """
    keyboard = [
        [
            InlineKeyboardButton("🇺🇸 English", callback_data='lang_en'),
            InlineKeyboardButton("🇮🇩 Bahasa Indonesia", callback_data='lang_id')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    sent_message = await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    store_message_id(user_id, sent_message.message_id)

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

def format_flight_status_message(flight_data, changes=None, language='en'):
    """Format flight status message with current data"""
    status_emoji = get_status_emoji(flight_data['flightstat'])

    message = f"✈️ {get_text('flight_info_title', language, flight_no=flight_data['flightno'])} Status*\n\n"
    message += f"{get_text('schedule_label', language)} {flight_data['schedule']}\n"
    message += f"{get_text('estimate_label', language)} {flight_data['estimate']}\n"
    message += f"{get_text('gate_label', language)} {flight_data['gatenumber']}\n"
    message += f"{get_text('status_label', language)} {status_emoji} {flight_data['flightstat']}\n"
    message += f"{get_text('route_label', language)} {flight_data['fromtolocation']}\n"

    if changes:
        message += f"\n{get_text('recent_changes', language)}\n"
        for change in changes:
            message += f"• {change}\n"

    message += f"\n{get_text('last_updated', language, time=datetime.now().strftime('%H:%M:%S'))}"

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

                                user_lang = monitoring_data.get('language', 'en')
                                sent_message = await bot.send_message(
                                    chat_id=user_id,
                                    text=(
                                        f"{get_text('flight_unavailable', user_lang, flight_no=monitoring_data['flight_no'], flight_id=flight_id)}\n\n"
                                        f"{get_text('last_known_status', user_lang)} {monitoring_data['last_status']}\n"
                                        f"{get_text('last_schedule', user_lang)} {monitoring_data['last_schedule']}\n"
                                        f"{get_text('last_estimate', user_lang)} {monitoring_data['last_estimate']}\n\n"
                                        f"{get_text('monitoring_continue', user_lang)}"
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

                            user_lang = monitoring_data.get('language', 'en')
                            notification_message = f"{get_text('flight_update_alert', user_lang)}\n\n"
                            notification_message += format_flight_status_message(current_flight, changes, user_lang)

                            keyboard = [
                                [InlineKeyboardButton(get_text('stop_monitoring', user_lang), callback_data=f"stop_monitor_{flight_id}")]
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

                    final_statuses = ['Departed, Gate Close']
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

                                user_lang = monitoring_data.get('language', 'en')
                                final_message = f"{get_text('final_status', user_lang, flight_no=current_flight['flightno'])}\n\n"
                                final_message += format_flight_status_message(current_flight, language=user_lang)
                                final_message += (
                                    f"\n\n{get_text('reached_final_status', user_lang, status=current_status)}\n"
                                    f"{get_text('program_exit', user_lang)}"
                                )
                                keyboard = [
                                    [InlineKeyboardButton(get_text('stop_monitoring', user_lang), callback_data=f"stop_monitor_{flight_id}")]
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