from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from flight_bot import FlightScheduleBot

flight_bot = FlightScheduleBot()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = """
🛫 *Selamat datang di Flight Schedule Bot!*

Saya dapat membantu Anda mencari informasi jadwal penerbangan.

*Cara penggunaan:*
• `/flight [kode_penerbangan] [tanggal]` - Cari penerbangan spesifik
• `/schedule [tanggal]` - Lihat jadwal penerbangan pada tanggal tertentu
• `/route [asal] [tujuan] [tanggal]` - Cari penerbangan berdasarkan rute
• `/help` - Bantuan penggunaan

*Contoh penggunaan:*
`/flight GA123 2024-07-20`
`/schedule 2024-07-20`
`/route CGK DPS 2024-07-20`
    """
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = """
🆘 *Bantuan Penggunaan Flight Schedule Bot*

*Perintah:*

1️⃣ `/flight [kode_penerbangan] [tanggal]`
   Mencari informasi penerbangan spesifik
   Contoh: `/flight GA123 2024-07-20`

2️⃣ `/schedule [tanggal]`
   Melihat jadwal penerbangan pada tanggal tertentu
   Contoh: `/schedule 2024-07-20`

3️⃣ `/route [asal] [tujuan] [tanggal]`
   Mencari penerbangan berdasarkan rute
   Contoh: `/route CGK DPS 2024-07-20`

4️⃣ `/help`
   Menampilkan pesan bantuan ini

*Format:*
• Tanggal: YYYY-MM-DD (tahun-bulan-hari)
• Kode penerbangan: GA123, QZ456, dll.
• Kode bandara: CGK, DPS, SUB, dll.

*Kode bandara:*
• CGK - Jakarta (Soekarno-Hatta)
• DPS - Denpasar (Ngurah Rai)
• SUB - Surabaya (Juanda)
• YIA - Yogyakarta
• PLM - Palembang
• PKU - Pekanbaru
• Dan lainnya...
    """
    await update.message.reply_text(help_message, parse_mode='Markdown')

async def flight_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text(
            "❌ Format salah!\n\n"
            "Gunakan: `/flight [kode_penerbangan] [tanggal]`\n"
            "Contoh: `/flight GA123 2024-07-20`",
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
            "Contoh: 2024-07-20"
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
✈️ *Informasi Penerbangan {flight_info['flight_code']}*

🏢 *Maskapai:* {flight_info['airline_name']}
📅 *Tanggal:* {flight_info['departure_time'].strftime('%d %B %Y')}

🛫 *Keberangkatan:*
• Bandara: {flight_info['origin_airport']} ({flight_info['origin_airport']})
• Kota: {flight_info['origin_city']}
• Waktu: {flight_info['departure_time'].strftime('%H:%M')} WIB

🛬 *Kedatangan:*
• Bandara: {flight_info['dest_airport']} ({flight_info['destination_airport']})
• Kota: {flight_info['dest_city']}
• Waktu: {flight_info['arrival_time'].strftime('%H:%M')} WIB

💺 *Kapasitas:* {flight_info['capacity']} penumpang
📊 *Status:* {status_emoji.get(flight_info['status'], '❓')} {flight_info['status']}
        """
        if flight_info.get('delay_minutes', 0) > 0:
            message += f"\n⏰ *Delay:* {flight_info['delay_minutes']} menit"
        if flight_info.get('gate'):
            message += f"\n🚪 *Gate:* {flight_info['gate']}"
        if flight_info.get('terminal'):
            message += f"\n🏢 *Terminal:* {flight_info['terminal']}"
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
            "Contoh: `/schedule 2024-07-20`",
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
            "Contoh: 2024-07-20"
        )
        return
    await update.message.reply_text("🔍 Mencari jadwal penerbangan...")
    flights = flight_bot.get_flights_by_date(date_str)
    if flights:
        message = f"📅 *Jadwal Penerbangan {date_obj.strftime('%d %B %Y')}*\n\n"
        for i, flight in enumerate(flights, 1):
            departure_time = flight['departure_time'].strftime('%H:%M')
            arrival_time = flight['arrival_time'].strftime('%H:%M')
            status_emoji = {
                'On Time': '✅',
                'Delayed': '⏰',
                'Cancelled': '❌',
                'Departed': '🛫',
                'Arrived': '🛬'
            }
            message += f"{i}. *{flight['flight_code']}* - {flight['airline_name']}\n"
            message += f"   {flight['origin_city']} ➡️ {flight['dest_city']}\n"
            message += f"   🕐 {departure_time} - {arrival_time} | {status_emoji.get(flight['status'], '❓')} {flight['status']}\n\n"
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
            "Contoh: `/route CGK DPS 2024-07-20`",
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
            "Contoh: 2024-07-20"
        )
        return
    await update.message.reply_text("🔍 Mencari penerbangan...")
    flights = flight_bot.get_flights_by_route(origin, destination, date_str)
    if flights:
        message = f"🛫 *Penerbangan {origin} ➡️ {destination}*\n"
        message += f"📅 *Tanggal:* {date_obj.strftime('%d %B %Y')}\n\n"
        for i, flight in enumerate(flights, 1):
            departure_time = flight['departure_time'].strftime('%H:%M')
            arrival_time = flight['arrival_time'].strftime('%H:%M')
            status_emoji = {
                'On Time': '✅',
                'Delayed': '⏰',
                'Cancelled': '❌',
                'Departed': '🛫',
                'Arrived': '🛬'
            }
            message += f"{i}. *{flight['flight_code']}* - {flight['airline_name']}\n"
            message += f"   🕐 {departure_time} - {arrival_time}\n"
            message += f"   📊 {status_emoji.get(flight['status'], '❓')} {flight['status']}\n\n"
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
            "🤖 Saya dapat membantu Anda mencari informasi penerbangan!\n\n"
            "Gunakan perintah:\n"
            "• `/flight [kode_penerbangan] [tanggal]` - Info penerbangan spesifik\n"
            "• `/schedule [tanggal]` - Jadwal penerbangan\n"
            "• `/route [asal] [tujuan] [tanggal]` - Penerbangan berdasarkan rute\n"
            "• `/help` - Bantuan lengkap",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "Maaf, saya tidak mengerti pesan Anda. 😅\n\n"
            "Ketik `/help` untuk melihat cara penggunaan bot ini."
        )