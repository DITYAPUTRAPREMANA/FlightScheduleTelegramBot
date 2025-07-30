from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from flight_bot import FlightScheduleBot

flight_bot = FlightScheduleBot()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = """
🛫 *Selamat datang di Flight Info Bot!*

Saya dapat membantu Anda mencari informasi jadwal penerbangan Secara real-time.

*Informasi Lebih Lengkap Gunakan:*
• `/help` - Bantuan penggunaan
    """
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = """
🆘 *Bantuan Penggunaan Flight Schedule Bot*

*Perintah:*

1. `/flight [kode_penerbangan] [tanggal]`
   Mencari informasi penerbangan spesifik
   Contoh: `/flight QZ-590 2025-07-29`

2. `/schedule [tanggal]`
   Melihat jadwal penerbangan pada tanggal tertentu
   Contoh: `/schedule 2025-07-29`

*Format:*
• Tanggal: YYYY-MM-DD (tahun-bulan-hari)
• Kode penerbangan: GA-123, QZ-456, dll.
• Kode bandara: CGK, DPS, SUB, dll.
    """
    await update.message.reply_text(help_message, parse_mode='Markdown')

async def flight_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text(
            "❌ Format salah!\n\n"
            "Gunakan: `/flight [kode_penerbangan] [tanggal]`\n"
            "Contoh: `/flight GA123 2024-01-15`",
            parse_mode='Markdown'
        )
        return

    flight_code = context.args[0].upper()
    date_str = context.args[1]
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        await update.message.reply_text(
            "❌ Format tanggal salah!\n\n"
            "Gunakan format: YYYY-MM-DD\n"
            "Contoh: 2024-01-15"
        )
        return
    await update.message.reply_text("🔍 Mencari informasi penerbangan...")
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
✈️ *Informasi Penerbangan {flight_info['flightno']}*

🏢 *Operator:* {flight_info['operator']}
📅 *Jadwal:* {flight_info['schedule']}
⏰ *Estimasi:* {flight_info['estimate']}

🚪 *Gate:* {flight_info['gatenumber']}
📊 *Status:* {status_emoji.get(flight_info['flightstat'], '❓')} {flight_info['flightstat']}
📍 *Rute:* {flight_info['fromtolocation']}
🌏 *Departure:* {flight_info.get('departure', '-')}
        """
        await update.message.reply_text(message, parse_mode='Markdown')
    else:
        await update.message.reply_text(
            f"❌ Penerbangan {flight_code} pada tanggal {date_str} tidak ditemukan.\n\n"
            "Pastikan kode penerbangan dan tanggal sudah benar."
        )

async def schedule_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text(
            "❌ Format salah!\n\n"
            "Gunakan: `/schedule [tanggal]`\n"
            "Contoh: `/schedule 2024-01-15`",
            parse_mode='Markdown'
        )
        return
    date_str = context.args[0]
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        await update.message.reply_text(
            "❌ Format tanggal salah!\n\n"
            "Gunakan format: YYYY-MM-DD\n"
            "Contoh: 2024-01-15"
        )
        return
    await update.message.reply_text("🔍 Mencari jadwal penerbangan...")
    flights = flight_bot.get_flights_by_date(date_str)
    if flights:
        message = f"📅 *Jadwal Penerbangan {date_obj.strftime('%d %B %Y')}*\n\n"
        for i, flight in enumerate(flights, 1):
            message += f"{i}. *{flight['flightno']}*\n"
            message += f"   📍 {flight['fromtolocation']}\n"
            message += f"   🌏 Departure: {flight.get('departure', '-')}\n\n"
        message += "💡 *Tip:* Gunakan `/flight [kode] [tanggal]` untuk detail lengkap"
        await update.message.reply_text(message, parse_mode='Markdown')
    else:
        await update.message.reply_text(
            f"❌ Tidak ada penerbangan pada tanggal {date_str}.\n\n"
            "Coba tanggal lain atau pastikan format tanggal sudah benar."
        )

async def route_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 3:
        await update.message.reply_text(
            "❌ Format salah!\n\n"
            "Gunakan: `/route [asal] [tujuan] [tanggal]`\n"
            "Contoh: `/route CGK DPS 2024-01-15`",
            parse_mode='Markdown'
        )
        return
    origin = context.args[0].upper()
    destination = context.args[1].upper()
    date_str = context.args[2]
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        await update.message.reply_text(
            "❌ Format tanggal salah!\n\n"
            "Gunakan format: YYYY-MM-DD\n"
            "Contoh: 2024-01-15"
        )
        return
    await update.message.reply_text("🔍 Mencari penerbangan...")
    flights = flight_bot.get_flights_by_route(origin, destination, date_str)
    if flights:
        message = f"🛫 *Penerbangan {origin} ➡️ {destination}*\n"
        message += f"📅 *Tanggal:* {date_obj.strftime('%d %B %Y')}\n\n"
        for i, flight in enumerate(flights, 1):
            status_emoji = {
                'On Time': '✅',
                'Delayed': '⏰',
                'Cancelled': '❌',
                'Departed': '🛫',
                'Arrived': '🛬'
            }
            message += f"{i}. *{flight['flightno']}* - {flight['operator']}\n"
            message += f"   📍 {flight['fromtolocation']}\n"
            message += f"   🕐 {flight['schedule']} | {status_emoji.get(flight['flightstat'], '❓')} {flight['flightstat']}\n"
            message += f"   🚪 Gate: {flight['gatenumber']}\n"
            message += f"   🌏 Departure: {flight.get('departure', '-')}\n\n"
        message += "💡 *Tip:* Gunakan `/flight [kode] [tanggal]` untuk detail lengkap"
        await update.message.reply_text(message, parse_mode='Markdown')
    else:
        await update.message.reply_text(
            f"❌ Tidak ada penerbangan dari {origin} ke {destination} pada tanggal {date_str}.\n\n"
            "Pastikan kode bandara dan tanggal sudah benar."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.lower()
    if any(keyword in message for keyword in ['flight', 'penerbangan', 'jadwal', 'schedule']):
        await update.message.reply_text(
            "🤖 Saya dapat membantu Anda mencari informasi penerbangan dari database real-time!\n\n"
            "Gunakan perintah:\n"
            "• `/flight [kode_penerbangan] [tanggal]` - Info penerbangan spesifik\n"
            "• `/schedule [tanggal]` - Jadwal penerbangan\n"
            "• `/route [asal] [tujuan] [tanggal]` - Penerbangan berdasarkan rute\n"
            "• `/help` - Bantuan lengkap\n\n"
            "*Contoh:* `/flight GA123 2024-01-15`",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "Maaf, saya tidak mengerti pesan Anda. 😅\n\n"
            "Ketik `/help` untuk melihat cara penggunaan bot ini."
        )