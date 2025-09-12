from typing import Dict, Any

TRANSLATIONS = {
    'en': {
        'welcome_title': '🛫 *Hello Passenger, Welcome to Flight Info Bot!*',
        'welcome_subtitle': 'I can help you find flight schedule information in real-time 😉',
        'select_flight_type': '*Please select the type of flights you want to monitor:*',
        'select_language': '*Please select your preferred language:*',

        'international': 'International',
        'domestic': 'Domestic',

        'english': 'English',
        'indonesian': 'Bahasa Indonesia',

        'schedule': '📅 Schedule',
        'search_flight': '🔍 Search Flight',
        'back_to_menu': '🏠 Back to Menu',
        'start_monitoring': 'Start Monitoring 🔔',
        'dont_monitor': "Don't Monitor",
        'stop_monitoring': '🚫 Stop Monitoring',

        'flight_selected': '✅ You selected to monitor {flight_type} flights.',
        'what_would_you_like': '🛫 What would you like to do?',
        'view_schedules': '• View flight schedules',
        'search_specific': '• Search for a specific flight',
        'flight_info_title': '✈️ Flight Information {flight_no}',
        'schedule_label': '📅 Schedule:',
        'estimate_label': '⏰ Estimate:',
        'gate_label': '🚪 Gate:',
        'status_label': '📦 Status:',
        'route_label': '📍 Route:',

        'monitoring_started': '✅ You are now monitoring flight {flight_no}!',
        'current_status': '📊 Current Status:',
        'monitoring_notifications': '🔔 You will receive notifications when the status or timing changes.',
        'monitoring_interval': '💡 Monitoring system will check for updates every 10 seconds.',
        'monitoring_stopped': '🚫 You have stopped monitoring flight {flight_no}.',
        'can_use_commands': '✅ You can now use all bot commands again. Type /start to begin.',

        'status_on_time': '✅',
        'status_delayed': '⏰',
        'status_cancelled': '❌',
        'status_departed': '🛫',
        'status_arrived': '🛬',
        'status_gate_close': '🚪',
        'status_boarding': '🎫',
        'status_checkin': '📋',

        'currently_monitoring': '⚠️ You are currently monitoring a flight. Please stop monitoring first using /stop_monitor before using other commands.',
        'select_flight_type_first': '❌ You need to select a flight type first! Please choose from Domestic or International by typing /start.',
        'incorrect_format': '❌ Incorrect format!',
        'use_flight_format': 'Use: /flight [Flight_Code]',
        'flight_not_found': '❌ Flight {flight_code} not found for today ({date}).',
        'no_flights_found': '❌ No {flight_type} flights found on {date}.',
        'check_flight_type': 'Please check the flight type or try again later.',
        'error_loading_schedules': '❌ Error loading flight schedules. Please try again.',
        'error_loading_flight_info': '❌ Error loading flight information. Please try again.',
        'no_active_monitoring': '❌ No active monitoring found.',
        'not_monitoring_any': '❌ You are not currently monitoring any flights.',

        'search_specific_flight': '🔍 Search for a Specific Flight',
        'enter_flight_code': 'Please enter the flight code in this format:',
        'flight_command_format': '`/flight [FLIGHT_CODE]`',
        'search_note': 'Note: The system will automatically search for today\'s flights.',
        'make_sure_selected': 'Make sure you\'ve selected {flight_type} flight type.',
        'search_again': '🔍 Search Again',

        'flight_schedules': '📅 Flight Schedules {date}',
        'no_flights_type': '❌ No flights of type {flight_type} on {date}.',

        'flight_update_alert': '🚨 Flight Update Alert!',
        'recent_changes': '🔄 *Recent Changes:*',
        'last_updated': '🕐 *Last Updated:* {time}',
        'flight_unavailable': '⚠️ Flight {flight_no} (ID: {flight_id}) is temporarily unavailable from the API.',
        'last_known_status': '📊 Last known status:',
        'last_schedule': '⏰ Last schedule:',
        'last_estimate': '🕐 Last estimate:',
        'monitoring_continue': '🔁 Monitoring will continue and retry automatically.',
        'final_status': '🏁 Flight {flight_no} - Final Status',
        'reached_final_status': '✅ Flight has reached final status ({status}). Monitoring has been automatically stopped.',
        'program_exit': '🔄 Program will now exit completely. Please restart with /start to begin again.',

        'debug_info': '🔍 Debug Information',
        'your_user_id': 'Your User ID:',
        'total_monitored': 'Total Monitored Flights:',
        'you_are_monitoring': '✅ *You are monitoring:*',
        'flight_id': 'Flight ID:',
        'notifications_sent': 'Notifications Sent:',
        'checks_performed': 'Checks Performed:',
        'last_seen': 'Last Seen:',
        'live_api_check': 'Live API Check:',
        'success': 'SUCCESS',
        'flight_not_found_debug': 'FLIGHT NOT FOUND',
        'error': 'ERROR',
        'not_monitoring_debug': '❌ You are not monitoring any flights',
        'all_monitored_users': 'All Monitored Users:',

        'test_notification': '🧪 Test Notification',
        'bot_can_send': '✅ Bot can send messages successfully!',
        'message_sent_at': 'Message sent at:',
        'failed_to_send': '❌ Failed to send notification:',

        'date_format': '%d %B %Y',
        'would_you_like_monitor': 'Would you like to monitor the status of this flight? You will receive updates if the status changes 😉',
        'searching_schedules': '🔍 Searching for Flight Schedules...',
        'language_changed': 'Language changed to {language_name}!'
    },

    'id': {
        'welcome_title': '🛫 *Halo Penumpang, Selamat Datang di Flight Info Bot!*',
        'welcome_subtitle': 'Saya dapat membantu Anda menemukan informasi jadwal penerbangan secara real-time 😉',
        'select_flight_type': '*Silakan pilih jenis penerbangan yang ingin Anda pantau:*',
        'select_language': '*Silakan pilih bahasa yang Anda inginkan:*',

        'international': 'Internasional',
        'domestic': 'Domestik',

        'english': 'English',
        'indonesian': 'Bahasa Indonesia',

        'schedule': '📅 Jadwal',
        'search_flight': '🔍 Cari Penerbangan',
        'back_to_menu': '🏠 Kembali ke Menu',
        'start_monitoring': 'Mulai Pantau 🔔',
        'dont_monitor': 'Jangan Pantau',
        'stop_monitoring': '🚫 Hentikan Pantauan',

        'flight_selected': '✅ Anda memilih untuk memantau penerbangan {flight_type}.',
        'what_would_you_like': '🛫 Apa yang ingin Anda lakukan?',
        'view_schedules': '• Lihat jadwal penerbangan',
        'search_specific': '• Cari penerbangan tertentu',
        'flight_info_title': '✈️ Informasi Penerbangan {flight_no}',
        'schedule_label': '📅 Jadwal:',
        'estimate_label': '⏰ Estimasi:',
        'gate_label': '🚪 Gerbang:',
        'status_label': '📦 Status:',
        'route_label': '📍 Rute:',

        'monitoring_started': '✅ Anda sekarang memantau penerbangan {flight_no}!',
        'current_status': '📊 Status Saat Ini:',
        'monitoring_notifications': '🔔 Anda akan menerima notifikasi ketika status atau waktu berubah.',
        'monitoring_interval': '💡 Sistem pemantauan akan memeriksa pembaruan setiap 10 detik.',
        'monitoring_stopped': '🚫 Anda telah menghentikan pemantauan penerbangan {flight_no}.',
        'can_use_commands': '✅ Anda sekarang dapat menggunakan semua perintah bot lagi. Ketik /start untuk memulai.',

        'status_on_time': '✅',
        'status_delayed': '⏰',
        'status_cancelled': '❌',
        'status_departed': '🛫',
        'status_arrived': '🛬',
        'status_gate_close': '🚪',
        'status_boarding': '🎫',
        'status_checkin': '📋',

        'currently_monitoring': '⚠️ Anda sedang memantau penerbangan. Silakan hentikan pemantauan terlebih dahulu menggunakan /stop_monitor sebelum menggunakan perintah lain.',
        'select_flight_type_first': '❌ Anda perlu memilih jenis penerbangan terlebih dahulu! Silakan pilih Domestik atau Internasional dengan mengetik /start.',
        'incorrect_format': '❌ Format tidak benar!',
        'use_flight_format': 'Gunakan: /flight [Kode_Penerbangan]',
        'flight_not_found': '❌ Penerbangan {flight_code} tidak ditemukan untuk hari ini ({date}).',
        'no_flights_found': '❌ Tidak ada penerbangan {flight_type} ditemukan pada {date}.',
        'check_flight_type': 'Silakan periksa jenis penerbangan atau coba lagi nanti.',
        'error_loading_schedules': '❌ Gagal memuat jadwal penerbangan. Silakan coba lagi.',
        'error_loading_flight_info': '❌ Gagal memuat informasi penerbangan. Silakan coba lagi.',
        'no_active_monitoring': '❌ Tidak ada pemantauan aktif ditemukan.',
        'not_monitoring_any': '❌ Anda tidak sedang memantau penerbangan apa pun.',

        'search_specific_flight': '🔍 Cari Penerbangan Tertentu',
        'enter_flight_code': 'Silakan masukkan kode penerbangan dengan format:',
        'flight_command_format': '`/flight [KODE_PENERBANGAN]`',
        'search_note': 'Catatan: Sistem akan otomatis mencari penerbangan hari ini.',
        'make_sure_selected': 'Pastikan Anda telah memilih jenis penerbangan {flight_type}.',
        'search_again': '🔍 Cari Lagi',

        'flight_schedules': '📅 Jadwal Penerbangan {date}',
        'no_flights_type': '❌ Tidak ada penerbangan jenis {flight_type} pada {date}.',

        'flight_update_alert': '🚨 Peringatan Pembaruan Penerbangan!',
        'recent_changes': '🔄 *Perubahan Terbaru:*',
        'last_updated': '🕐 *Terakhir Diperbarui:* {time}',
        'flight_unavailable': '⚠️ Penerbangan {flight_no} (ID: {flight_id}) sementara tidak tersedia dari API.',
        'last_known_status': '📊 Status terakhir yang diketahui:',
        'last_schedule': '⏰ Jadwal terakhir:',
        'last_estimate': '🕐 Estimasi terakhir:',
        'monitoring_continue': '🔁 Pemantauan akan dilanjutkan dan mencoba ulang secara otomatis.',
        'final_status': '🏁 Penerbangan {flight_no} - Status Akhir',
        'reached_final_status': '✅ Penerbangan telah mencapai status akhir ({status}). Pemantauan telah dihentikan secara otomatis.',
        'program_exit': '🔄 Program akan keluar sepenuhnya. Silakan restart dengan /start untuk memulai lagi.',

        'debug_info': '🔍 Informasi Debug',
        'your_user_id': 'ID Pengguna Anda:',
        'total_monitored': 'Total Penerbangan yang Dipantau:',
        'you_are_monitoring': '✅ *Anda sedang memantau:*',
        'flight_id': 'ID Penerbangan:',
        'notifications_sent': 'Notifikasi Terkirim:',
        'checks_performed': 'Pemeriksaan Dilakukan:',
        'last_seen': 'Terakhir Dilihat:',
        'live_api_check': 'Pemeriksaan API Langsung:',
        'success': 'BERHASIL',
        'flight_not_found_debug': 'PENERBANGAN TIDAK DITEMUKAN',
        'error': 'KESALAHAN',
        'not_monitoring_debug': '❌ Anda tidak sedang memantau penerbangan apa pun',
        'all_monitored_users': 'Semua Pengguna yang Dipantau:',

        'test_notification': '🧪 Notifikasi Uji',
        'bot_can_send': '✅ Bot dapat mengirim pesan dengan sukses!',
        'message_sent_at': 'Pesan dikirim pada:',
        'failed_to_send': '❌ Gagal mengirim notifikasi:',

        'date_format': '%d %B %Y',
        'would_you_like_monitor': 'Apakah Anda ingin memantau status penerbangan ini? Anda akan menerima pembaruan jika status berubah 😉',
        'searching_schedules': '🔍 Mencari Jadwal Penerbangan...',
        'language_changed': 'Bahasa diubah ke {language_name}!'
    }
}

def get_text(key: str, language: str = 'en', **kwargs) -> str:
    """Get translated text for a given key and language"""
    if language not in TRANSLATIONS:
        language = 'en'
    text = TRANSLATIONS[language].get(key, TRANSLATIONS['en'].get(key, key))
    try:
        return text.format(**kwargs)
    except (KeyError, ValueError):
        return text

def get_status_emoji(status: str) -> str:
    """Get emoji for flight status"""
    status_lower = status.lower() if status else ''
    if 'on time' in status_lower:
        return '✅'
    elif 'delayed' in status_lower:
        return '⏰'
    elif 'cancelled' in status_lower:
        return '❌'
    elif 'departed' in status_lower:
        return '🛫'
    elif 'arrived' in status_lower:
        return '🛬'
    elif 'gate close' in status_lower:
        return '🚪'
    elif 'boarding' in status_lower:
        return '🎫'
    elif 'check-in' in status_lower:
        return '📋'
    else:
        return '📊'

def get_month_names(language: str = 'en') -> Dict[str, str]:
    """Get month names for date formatting"""
    if language == 'id':
        return {
            'January': 'Januari', 'February': 'Februari', 'March': 'Maret',
            'April': 'April', 'May': 'Mei', 'June': 'Juni',
            'July': 'Juli', 'August': 'Agustus', 'September': 'September',
            'October': 'Oktober', 'November': 'November', 'December': 'Desember'
        }
    return {}
