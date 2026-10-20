import os
import json
import time
import subprocess
import requests

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown

# Inisialisasi Console Rich
console = Console()

# Batas maksimal pesan dikurangi ke 15 agar total token tetap irit
MAX_MESSAGES = 15

# 1. Bersihkan layar awal
console.clear()

# Fungsi membaca variabel dari file .env secara manual
def load_env_file(filepath="~/.env"):
    env_path = os.path.expanduser(filepath)
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    env_vars[key.strip()] = val.strip().strip("'\"")
    return env_vars

# Load API Key dari .env atau environment system
env_vars = load_env_file("~/.env")
API_KEY = env_vars.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    console.print(Panel("[bold red]❌ Error: OPENROUTER_API_KEY tidak ditemukan di ~/.env![/bold red]", border_style="red"))
    exit(1)

URL = "https://openrouter.ai/api/v1/chat/completions"
HISTORY_FILE = os.path.expanduser("~/agent_history.json")

# FUNGSI OTOMATIS CARI MODEL GRATIS DARI OPENROUTER
def fetch_free_models():
    try:
        res = requests.get("https://openrouter.ai/api/v1/models", timeout=10)
        if res.status_code == 200:
            data = res.json().get("data", [])
            # Filter model yang harganya 0 (gratis) atau memiliki akhiran :free
            free_list = [
                m["id"] for m in data 
                if m.get("id", "").endswith(":free") or 
                (m.get("pricing", {}).get("prompt") == "0" and m.get("pricing", {}).get("completion") == "0")
            ]
            if free_list:
                return free_list
    except Exception:
        pass
    
    # Fallback daftar model gratis default jika request daftar model gagal/timeout
    return [
        "meta-llama/llama-3.3-70b-instruct:free",
        "qwen/qwen-2.5-coder-32b-instruct:free",
        "google/gemini-flash-1.5-exp:free",
        "deepseek/deepseek-chat:free"
    ]

# Dapatkan daftar model gratis otomatis
AVAILABLE_FREE_MODELS = fetch_free_models()
CURRENT_MODEL_INDEX = 0
MODEL = AVAILABLE_FREE_MODELS[CURRENT_MODEL_INDEX]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

system_prompt = (
    "Kamu adalah AI Agent asisten khusus di lingkungan Termux Android. "
    "Kamu punya akses untuk mengeksekusi perintah bash di terminal Termux. "
    "Setiap kali kamu memberikan instruksi yang perlu dijalankan di terminal, tuliskan perintah tersebut "
    "di dalam blok kode ```bash ... ```. "
    "Sistem akan otomatis mengeksekusi perintah tersebut dan memberikan hasilnya padamu."
)

# Fungsi memangkas riwayat agar token tetap irit
def trim_memory(messages_list, max_limit=MAX_MESSAGES):
    if len(messages_list) > max_limit:
        trimmed = [messages_list[0]] + messages_list[-(max_limit - 1):]
        console.print(f"[dim yellow]✂️ Riwayat pesan dipotong otomatis ke {max_limit} pesan terakhir untuk menghemat token.[/dim yellow]")
        return trimmed
    return messages_list

def load_memory():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                saved_messages = json.load(f)
                if saved_messages and saved_messages[0].get("role") == "system":
                    return trim_memory(saved_messages)
        except Exception as e:
            console.print(f"[bold yellow]⚠️ Gagal memuat memory:[/bold yellow] {e}")
    return [{"role": "system", "content": system_prompt}]

def save_memory(messages_list):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(messages_list, f, ensure_ascii=False, indent=2)
    except Exception as e:
        console.print(f"[bold red]⚠️ Gagal menyimpan memory:[/bold red] {e}")

# Splash Screen Loading
with console.status("[bold cyan]🔄 Mencari model gratis aktif & memuat sistem...[/bold cyan]", spinner="dots"):
    time.sleep(1.2)
    messages = load_memory()

console.clear()

# Header Banner
console.print(
    Panel.fit(
        "[bold cyan]🤖 TERMUX AUTONOMOUS AI v2.0[/bold cyan]\n"
        f"[dim]• Model Gratis Terdeteksi: [bold green]{MODEL}[/bold green] ({len(AVAILABLE_FREE_MODELS)} ditemukan)[/dim]\n"
        "[italic bright_black]• Ketik 'exit' untuk keluar | 'clear' untuk reset memory[/italic bright_black]",
        border_style="cyan",
        padding=(0, 2)
    )
)

if len(messages) > 1:
    console.print(f"[dim italic green]🧠 Memuat riwayat percakapan ({len(messages) - 1} pesan tersimpan)[/dim italic green]")

while True:
    try:
        user_input = console.input("\n[bold green]>[/bold green] ")
        
        if user_input.strip().lower() in ['exit', 'q']:
            save_memory(messages)
            console.print(Panel("[bold green]Memory tersimpan aman! Sampai jumpa 👋[/bold green]", border_style="green"))
            break
            
        if user_input.strip().lower() == 'clear':
            messages = [{"role": "system", "content": system_prompt}]
            save_memory(messages)
            console.clear()
            console.print(
                Panel.fit(
                    "[bold cyan]🤖 TERMUX AUTONOMOUS AI v2.0[/bold cyan]\n"
                    f"[dim]• Model Gratis Terdeteksi: [bold green]{MODEL}[/bold green][/dim]\n"
                    "[italic bright_black]• Ketik 'exit' untuk keluar | 'clear' untuk reset memory[/italic bright_black]",
                    border_style="cyan",
                    padding=(0, 2)
                )
            )
            console.print(Panel("[bold yellow]🧹 Ingatan dibersihkan! Memulai sesi baru dari nol.[/bold yellow]", border_style="yellow"))
            continue

        if not user_input.strip():
            continue

        # Render Bubble Chat User
        console.print(
            Panel(
                Text(user_input, style="bold white"),
                title="[bold green]👤 Kamu[/bold green]",
                title_align="left",
                border_style="green",
                padding=(0, 1)
            )
        )

        messages.append({"role": "user", "content": user_input})
        messages = trim_memory(messages)
        save_memory(messages)

        while True:
            payload = {
                "model": MODEL,
                "messages": messages,
                "max_tokens": 1500
            }

            time.sleep(2)

            with console.status(f"[bold cyan]AI ({MODEL.split('/')[-1]}) berpikir...[/bold cyan]", spinner="dots"):
                response = requests.post(URL, headers=headers, json=payload)

            # AUTOMATIC RETRY / AUTO-SWITCH JIKA MODEL TERKENA RATE LIMIT / ERROR 404 / 402
            if response.status_code in [402, 404]:
                CURRENT_MODEL_INDEX = (CURRENT_MODEL_INDEX + 1) % len(AVAILABLE_FREE_MODELS)
                OLD_MODEL = MODEL
                MODEL = AVAILABLE_FREE_MODELS[CURRENT_MODEL_INDEX]
                console.print(f"[dim yellow]🔄 Model {OLD_MODEL.split('/')[-1]} bermasalah. Otomatis beralih ke -> [bold green]{MODEL}[/bold green]...[/dim yellow]")
                time.sleep(3)
                continue

            if response.status_code != 200:
                console.print(Panel(f"[bold red]API Error [{response.status_code}]:[/bold red]\n{response.text}", border_style="red"))
                break

            result = response.json()
            
            try:
                reply = result['choices'][0]['message'].get('content')
            except (KeyError, IndexError):
                reply = None

            if not reply:
                reply = "[Gagal menerima respon teks dari AI. Silakan coba kirim ulang pesan.]"
            
            # Render Bubble Chat AI
            console.print(
                Panel(
                    Markdown(reply),
                    title=f"[bold cyan]AI ({MODEL.split('/')[-1]}) 🤖[/bold cyan]",
                    title_align="right",
                    border_style="cyan",
                    padding=(0, 1)
                )
            )
            
            messages.append({"role": "assistant", "content": reply})
            messages = trim_memory(messages)
            save_memory(messages)

            # Cek jika ada eksekusi bash
            if "```bash" in reply:
                cmd = reply.split("```bash")[1].split("```")[0].strip()
                
                alert_content = (
                    f"[bold yellow]⚠️ PERINGATAN EKSEKUSI PERINTAH[/bold yellow]\n\n"
                    f"[white]AI meminta izin untuk menjalankan instruksi di Termux:[/white]\n\n"
                    f"[bold green]$ {cmd}[/bold green]"
                )
                
                console.print(
                    Panel(
                        alert_content,
                        title="[bold yellow]◢◤ KRUSIAL ◢◤[/bold yellow]",
                        title_align="center",
                        border_style="yellow",
                        padding=(1, 2)
                    )
                )

                confirm = console.input("\n[bold yellow]❓ Jalankan perintah ini di Termux? (y/n)[/bold yellow] [dim]>[/dim] ").strip().lower()

                if confirm == 'y':
                    try:
                        with console.status("[bold magenta]⚙️ Menjalankan perintah di terminal...[/bold magenta]", spinner="dots"):
                            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
                        
                        console.print(
                            Panel(
                                Text(output if output else "Perintah berhasil dieksekusi (tanpa output).", style="bright_white"),
                                title="[bold magenta]🖥️ Output Terminal[/bold magenta]",
                                title_align="left",
                                border_style="magenta",
                                padding=(0, 1)
                            )
                        )
                        
                        trimmed_output = output[:800] + ("\n... [Output dipotong pendek untuk menghemat token]" if len(output) > 800 else "")
                        messages.append({"role": "user", "content": f"Hasil eksekusi perintah `{cmd}`:\n{trimmed_output}"})
                        messages = trim_memory(messages)
                        save_memory(messages)
                        
                        time.sleep(3)
                        continue
                        
                    except subprocess.CalledProcessError as e:
                        error_out = e.output[:800] + ("\n... [Output error dipotong]" if len(e.output) > 800 else "")
                        console.print(
                            Panel(
                                Text(e.output, style="bold red"),
                                title="[bold red]❌ Error Terminal[/bold red]",
                                title_align="left",
                                border_style="red"
                            )
                        )
                        messages.append({"role": "user", "content": f"Gagal mengeksekusi `{cmd}`. Error:\n{error_out}"})
                        messages = trim_memory(messages)
                        save_memory(messages)
                        
                        time.sleep(3)
                        continue
                else:
                    console.print("[dim yellow]Eksekusi dibatalkan oleh pengguna.[/dim yellow]")
            break

    except KeyboardInterrupt:
        save_memory(messages)
        console.print("\n[bold yellow]Memory tersimpan. Keluar dari sistem.[/bold yellow]")
        break
    except Exception as e:
        console.print(f"\n[bold red]System Error:[/bold red] {e}")
