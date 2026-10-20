# 🤖 Termux Autonomous AI Agent v2.0

Asisten AI Otonom berbasis CLI yang dirancang khusus untuk lingkungan **Termux Android**. Dilengkapi dengan antarmuka visual Rich TUI, pemangkasan memori otomatis, eksekusi perintah terminal mandiri, dan integrasi API OpenRouter.

---

## ✨ Fitur Utama

* **Autonomous Terminal Execution**: Mampu menjalankan instruksi perintah `bash` di Termux secara otomatis dengan konfirmasi keamanan interaktif ($y/n$).
* **Auto-Detect & Fallback Free Models**: Mengidentifikasi dan memilih model gratisan yang aktif di OpenRouter secara otomatis, serta mendukung *auto-fallback* jika terjadi error rate-limit/kredit (402/404).
* **Token Saver & Sliding Window Memory**: Mengatur riwayat pesan dengan metode *sliding window* (`MAX_MESSAGES = 15`) dan pemotongan output terminal (max 800 karakter) untuk mencegah pembengkakan token.
* **Rich Visual TUI**: Antarmuka terminal modern menggunakan library `rich` (Bubble Chat Panel, Markdown Renderer, Spinner Status).
* **Persistent Long-Term Memory**: Menyimpan dan memuat riwayat percakapan secara lokal di `~/agent_history.json`.

---

## 📋 Prasyarat

* Python 3
* Git
* Package `requests` & `rich`

---

## 🚀 Panduan Instalasi & Penggunaan

### 1. Clone Repositori
```bash
git clone [https://github.com/hadi-exx/Agent.git](https://github.com/hadi-exx/Agent.git)
cd Agent
```

### 2. Install Dependensi
```bash
pip install requests rich
```

### 3. Konfigurasi API Key
Buat file `~/.env` dan masukkan **OpenRouter API Key** kamu:
```bash
echo "OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxx" > ~/.env
```

### 4. Jalankan AI Agent
```bash
python agent2.py
```

---

## 💡 Perintah Dalam Aplikasi

* `clear` : Mereduksi/membersihkan ingatan percakapan dan memulai sesi baru dari nol.
* `exit` atau `q` : Menyimpan riwayat percakapan ke memori lokal lalu keluar dari aplikasi.

---

## 🛡️ Lisensi & Kepatuhan
Diperuntukkan untuk penggunaan pribadi dan pengembangan eksperimental di lingkungan Termux Android.
