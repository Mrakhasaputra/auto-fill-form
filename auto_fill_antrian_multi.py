"""
auto_fill_antrian_multi_keep_open.py (v2)
-----------------------------------
🌀 Loop terus-menerus sampai form aktif.
🧩 Membuka 3 form sekaligus dan TIDAK menutup browser.
💡 Setelah submit, tab/Chrome tetap terbuka (HEADLESS must be False).
"""

import time
import random
import requests
import threading
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---------------- CONFIG ----------------
TARGET_URL = "https://www.antributikbekasi.com/"

USERS = [
    # {"name": "DEWI AGUSTINA SUSANTI", "ktp": "3271025208960006", "phone": "089608678980"},
    # {"name": "BERLINTAN JAYANTI", "ktp": "3201016003910011", "phone": "082299560210"},
    # {"name": "TUTUT WAHYUNI", "ktp": "3275075403790021", "phone": "081388344936"},
    {"name": "TIARA", "ktp": "3275076408050001", "phone": "085945830366"},
    {"name": "MUHAMMAD FAIZ RAMADHAN", "ktp": "3171051611030001", "phone": "08111965944"},
    {"name": "YENI MARLINA", "ktp": "0375074105880010", "phone": "082111516100"},
]

HEADLESS = False   # HARUS False agar browser terlihat
FAST_MODE = True
REQUEST_TIMEOUT = 1
CHECK_INTERVAL = 1  # detik antar pengecekan
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

OPEN_DRIVERS = []
# ----------------------------------------


def human_delay(min_s=0.02, max_s=0.15):
    if FAST_MODE:
        time.sleep(0.01)
    else:
        time.sleep(random.uniform(min_s, max_s))


def page_has_form(url: str) -> bool:
    """Cek apakah halaman berisi form target."""
    try:
        headers = {"User-Agent": USER_AGENT}
        resp = requests.get(url, timeout=REQUEST_TIMEOUT, headers=headers)
        if resp.status_code != 200:
            return False
        soup = BeautifulSoup(resp.text, "html.parser")
        return bool(
            soup.find(id="name") or soup.find(id="ktp") or soup.find(id="phone_number")
        )
    except requests.RequestException:
        return False


def run_selenium_fill(user):
    """Jalankan Chrome & isi form untuk 1 user."""
    name, ktp, phone = user["name"], user["ktp"], user["phone"]

    chrome_opts = Options()
    if HEADLESS:
        chrome_opts.add_argument("--headless=new")

    # Optimasi Chrome
    chrome_opts.add_argument("--disable-gpu")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")
    chrome_opts.add_argument("--disable-blink-features=AutomationControlled")
    chrome_opts.add_argument("--blink-settings=imagesEnabled=false")
    chrome_opts.add_argument("--log-level=3")
    chrome_opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_opts.add_argument("--window-size=1200,800")

    driver = webdriver.Chrome(options=chrome_opts)
    wait = WebDriverWait(driver, 10)

    try:
        driver.get(TARGET_URL)
        print(f"[i] Membuka halaman untuk {name}")
        wait.until(EC.presence_of_element_located((By.ID, "name")))

        try:
            el_name = driver.find_element(By.ID, "name")
            el_name.clear()
            el_name.send_keys(name)
        except Exception:
            print(f"[!] input 'name' tidak ditemukan untuk {name}")

        try:
            el_ktp = driver.find_element(By.ID, "ktp")
            el_ktp.clear()
            el_ktp.send_keys(ktp)
        except Exception:
            print(f"[!] input 'ktp' tidak ditemukan untuk {name}")

        try:
            el_phone = driver.find_element(By.ID, "phone_number")
            el_phone.clear()
            el_phone.send_keys(phone)
        except Exception:
            print(f"[!] input 'phone_number' tidak ditemukan untuk {name}")

        print(f"[+] Data diisi untuk {name}")

        # Centang checkbox bila ada
        for cid in ["check", "check_2"]:
            try:
                checkbox = wait.until(EC.element_to_be_clickable((By.ID, cid)))
                driver.execute_script("arguments[0].click();", checkbox)
            except Exception:
                pass

        print("[✓] Checkbox dicentang (jika ada)")

        # CAPTCHA
        try:
            captcha_box = driver.find_element(By.ID, "captcha-box")
            visible_text = (captcha_box.text or "").strip()
            if visible_text:
                try:
                    driver.find_element(By.ID, "captcha_input").send_keys(visible_text)
                    print(f"[+] CAPTCHA otomatis diisi: {visible_text}")
                except Exception:
                    print("[!] CAPTCHA teks ditemukan tapi input tidak tersedia.")
            else:
                print(f"[!] CAPTCHA mungkin gambar/reCAPTCHA — isi manual.")
                try:
                    captcha_input = driver.find_element(By.ID, "captcha_input")
                    driver.execute_script("arguments[0].focus();", captcha_input)
                except Exception:
                    pass
        except Exception:
            print("[i] Tidak menemukan elemen CAPTCHA, lanjut.")

        # Submit form
        try:
            daftar_btn = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Daftar') or @type='submit']")
                )
            )
            driver.execute_script("arguments[0].click();", daftar_btn)
            print(f"[✓] Submit diklik untuk {name}")
        except Exception as e:
            print(f"[!] Gagal klik submit untuk {name}: {e}")

        time.sleep(2)
        print(f"[i] Selesai proses untuk {name} — URL: {driver.current_url}")

        OPEN_DRIVERS.append({"name": name, "driver": driver})
        print(f"[i] Browser untuk {name} dibiarkan terbuka. (Total open: {len(OPEN_DRIVERS)})")

    except Exception as e:
        print(f"[!] Error {name}: {e}")


def close_all():
    """Tutup semua browser yang masih terbuka."""
    print("[i] Menutup semua browser...")
    for item in OPEN_DRIVERS:
        try:
            item["driver"].quit()
        except Exception:
            pass
    OPEN_DRIVERS.clear()
    print("[i] Semua browser ditutup.")


def main():
    print(f"[i] Mengecek halaman: {TARGET_URL}")
    while True:
        if page_has_form(TARGET_URL):
            print("[✓] Form aktif! Membuka 3 form sekaligus...\n")
            break
        else:
            print(f"[i] Form belum aktif. Coba lagi dalam {CHECK_INTERVAL} detik...\n")
            time.sleep(CHECK_INTERVAL)

    threads = []
    for user in USERS:
        t = threading.Thread(target=run_selenium_fill, args=(user,))
        t.start()
        threads.append(t)
        time.sleep(0.8)

    for t in threads:
        t.join()

    print("\n[🎉] Semua form sudah diisi dan browser dibiarkan terbuka.")
    print("[i] Biarkan terminal ini terbuka agar browser tetap hidup.")
    print("[i] Ketik 'close' untuk menutup semua browser atau tekan Ctrl+C untuk keluar.")

    try:
        while True:
            cmd = input("> ").strip().lower()
            if cmd in ("close", "quit", "exit"):
                close_all()
                break
            elif cmd == "list":
                print("Browser terbuka:")
                for idx, it in enumerate(OPEN_DRIVERS, 1):
                    print(f"{idx}. {it['name']}")
            else:
                print("Perintah: list | close | quit")
    except KeyboardInterrupt:
        print("\n[i] Ctrl+C diterima — browser tetap terbuka.")


if __name__ == "__main__":
    main()
