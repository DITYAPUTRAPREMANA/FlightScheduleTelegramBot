## 🏗️ Struktur Program
flight-schedule-bot/
├── main.py             # Entry point & bot initialization
├── flight_bot.py       # Core flight data logic
├── flight_handler.py   # Telegram bot handlers
├── language.py         # Multi-language support
├── config.py           # Configuration management
├── health.py           # Health check API
├── requirements.txt    # Dependencies
├── Dockerfile          # Container configuration
└── docker-compose.yml  # Orchestration
```

## 🔧 Penjelasan Per Fungsi

### 📁 **main.py**

#### `main()`
- **Fungsi**: Entry point utama aplikasi
- **Tugas**:
  - Inisialisasi bot Telegram
  - Registrasi command handlers
  - Menjalankan thread monitoring dan health server
  - Mengatur polling bot

#### `run_monitoring_loop(application)`
- **Fungsi**: Menjalankan loop monitoring dalam thread terpisah
- **Tugas**:
  - Membuat event loop baru
  - Menjalankan `monitor_flight_status()`
  - Error handling untuk thread monitoring

#### `run_health_server()`
- **Fungsi**: Menjalankan health check server
- **Tugas**:
  - Konfigurasi FastAPI server
  - Menjalankan server di port 8000
  - Health check endpoint

### 📁 **flight_handler.py**

#### **Fungsi Utilitas**###

##### `is_user_monitoring(user_id)`
- **Fungsi**: Mengecek apakah user sedang monitoring penerbangan
- **Return**: Boolean
- **Parameter**: `user_id` - ID user Telegram

##### `auto_delete_previous_message(bot, user_id, chat_id)`
- **Fungsi**: Menghapus pesan sebelumnya untuk mencegah penumpukan
- **Tugas**:
  - Mencari message ID dari history
  - Menghapus pesan lama
  - Error handling jika gagal hapus

##### `store_message_id(user_id, message_id)`
- **Fungsi**: Menyimpan message ID untuk auto-delete
- **Tugas**: Menyimpan mapping user_id → message_id

##### `safe_edit_message(query, text, reply_markup, parse_mode)`
- **Fungsi**: Edit pesan dengan error handling
- **Tugas**:
  - Coba edit pesan existing
  - Jika gagal, hapus pesan lama dan kirim pesan baru
  - Fallback mechanism

#### **Command Handlers**###

##### `start(update, context)`
- **Fungsi**: Handler untuk command `/start`
- **Tugas**:
  - Cek apakah user sedang monitoring
  - Tampilkan menu pilih bahasa jika belum set
  - Tampilkan menu pilih jenis penerbangan
  - Auto-delete pesan sebelumnya

##### `flight_info(update, context)`
- **Fungsi**: Handler untuk command `/flight [nomor_penerbangan]`
- **Tugas**:
  - Validasi format input
  - Cari informasi penerbangan
  - Tampilkan info lengkap (jadwal, estimasi, gate, status, rute)
  - Tampilkan tombol monitoring
  - Validasi jenis penerbangan (domestik/internasional)

##### `schedule_info(update, context)`
- **Fungsi**: Handler untuk command `/schedule [tanggal]`
- **Tugas**:
  - Validasi format tanggal (YYYY-MM-DD)
  - Ambil data penerbangan berdasarkan tanggal
  - Filter berdasarkan jenis penerbangan
  - Tampilkan maksimal 20 penerbangan
  - Format tanggal sesuai bahasa

##### `stop_monitor(update, context)`
- **Fungsi**: Handler untuk command `/stop_monitor`
- **Tugas**:
  - Hentikan monitoring user
  - Hapus dari daftar monitored_flights
  - Konfirmasi ke user

##### `debug_monitor(update, context)`
- **Fungsi**: Handler untuk command `/debug`
- **Tugas**:
  - Tampilkan informasi debug
  - Status monitoring user
  - Jumlah notifikasi yang dikirim
  - Test koneksi API live

##### `change_language(update, context)`
- **Fungsi**: Handler untuk command `/language`
- **Tugas**:
  - Ubah preferensi bahasa user
  - Tampilkan menu pilih bahasa
  - Update user_data

#### **Button Handlers** ###

##### `button(update, context)`
- **Fungsi**: Handler untuk semua callback query (tombol inline)
- **Tugas**:
  - Parse callback data
  - Route ke handler yang sesuai
  - Handle pilihan bahasa, jenis penerbangan, monitoring, dll

##### `show_flight_type_selection(update, context, language)`
- **Fungsi**: Tampilkan menu pilih jenis penerbangan
- **Tugas**:
  - Tampilkan tombol Domestic/International
  - Sesuaikan bahasa
  - Auto-delete pesan sebelumnya

##### `handle_schedule_request(query, flight_type, date_str, user_id, context)`
- **Fungsi**: Handle tombol lihat jadwal
- **Tugas**:
  - Ambil data penerbangan berdasarkan tanggal
  - Filter berdasarkan jenis penerbangan
  - Format tanggal sesuai bahasa
  - Tampilkan maksimal 20 penerbangan

##### `handle_search_flight_request(query, flight_type, user_id, context)`
- **Fungsi**: Handle tombol cari penerbangan
- **Tugas**:
  - Tampilkan instruksi pencarian
  - Format command yang benar
  - Validasi jenis penerbangan

##### `handle_flight_search_result(query, flight_code, date_str, user_id, flight_type, context)`
- **Fungsi**: Handle hasil pencarian penerbangan
- **Tugas**:
  - Cari informasi penerbangan
  - Tampilkan info lengkap jika ditemukan
  - Tampilkan tombol monitoring
  - Handle jika tidak ditemukan

##### `handle_back_to_menu(query, context)`
- **Fungsi**: Handle tombol kembali ke menu
- **Tugas**:
  - Cek status monitoring user
  - Tampilkan menu utama
  - Navigasi yang konsisten

#### **Monitoring Functions**

##### `monitor_flight_status(application)`
- **Fungsi**: Loop monitoring real-time utama
- **Tugas**:
  - Loop kontinyu setiap 10 detik
  - Cek perubahan status untuk semua user
  - Deteksi perubahan: status, jadwal, estimasi, gate
  - Kirim notifikasi jika ada perubahan
  - Handle final status (Departed, Gate Close)
  - Auto-stop monitoring jika final status

##### `format_flight_status_message(flight_data, changes, language)`
- **Fungsi**: Format pesan status penerbangan
- **Tugas**:
  - Format pesan dengan emoji status
  - Tampilkan perubahan yang terjadi
  - Timestamp update
  - Konsisten dengan bahasa

#### **Utility Functions** ###

##### `normalize_value(value)`
- **Fungsi**: Normalisasi nilai untuk perbandingan
- **Tugas**:
  - Handle None values
  - Strip whitespace
  - Convert ke string

##### `safe_string_compare(val1, val2)`
- **Fungsi**: Perbandingan string yang aman
- **Tugas**:
  - Normalisasi kedua nilai
  - Perbandingan yang robust
  - Handle edge cases

##### `normalize_status(value)`
- **Fungsi**: Normalisasi status untuk perbandingan
- **Tugas**:
  - Convert ke lowercase
  - Handle None values
  - Konsistensi format

### 📁 **flight_bot.py**

#### `FlightScheduleBot` Class

##### `__init__()`
- **Fungsi**: Inisialisasi class
- **Tugas**: Setup basic configuration

##### `_fetch_api(url)`
- **Fungsi**: Fetch data dari API eksternal
- **Tugas**:
  - HTTP GET request dengan timeout
  - Error handling untuk network issues
  - Return JSON data atau None

##### `_normalize_flights(data, departure)`
- **Fungsi**: Normalisasi data penerbangan dari API
- **Tugas**:
  - Extract data dari response API
  - Standardisasi format data
  - Tambahkan informasi departure type
  - Filter data yang valid

##### `_get_all_flights_for_date(date)`
- **Fungsi**: Ambil semua penerbangan untuk tanggal tertentu
- **Tugas**:
  - Fetch data domestik dan internasional
  - Normalisasi data
  - Filter berdasarkan tanggal
  - Sort berdasarkan jadwal

##### `get_flights_by_date(date)`
- **Fungsi**: Public method untuk ambil penerbangan per tanggal
- **Return**: List of flight dictionaries

##### `get_flight_info(flight_code, date)`
- **Fungsi**: Cari informasi penerbangan spesifik
- **Tugas**:
  - Cari berdasarkan nomor penerbangan
  - Case insensitive search
  - Return flight info atau None

##### `get_flight_info_by_id(flight_id)`
- **Fungsi**: Cari penerbangan berdasarkan ID
- **Tugas**:
  - Cari di data domestik dan internasional
  - Return flight info atau None

### 📁 **config.py**

#### Environment Variables
- **BOT_TOKEN**: Token bot Telegram
- **API_DOM_URL**: URL API penerbangan domestik
- **API_INTER_URL**: URL API penerbangan internasional
- **MONITOR_INTERVAL_SECONDS**: Interval monitoring (default: 10)
- **LOG_LEVEL**: Level logging (default: INFO)

### 📁 **health.py**

#### `app` (FastAPI instance)
- **Fungsi**: Health check endpoint
- **Endpoint**: `/health`
- **Return**: `{"status": "ok"}`
- **Tujuan**: Docker health check

### 📁 **language.py`

#### `get_text(key, language, **kwargs)`
- **Fungsi**: Ambil teks berdasarkan bahasa
- **Tugas**:
  - Lookup teks dari TRANSLATIONS
  - Format string dengan parameter
  - Fallback ke bahasa default

#### `get_status_emoji(status)`
- **Fungsi**: Ambil emoji berdasarkan status penerbangan
- **Tugas**: Mapping status ke emoji yang sesuai

#### `get_month_names(language)`
- **Fungsi**: Ambil nama bulan berdasarkan bahasa
- **Tugas**: Mapping nama bulan Inggris ke Indonesia