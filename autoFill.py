"""
auto_fill_antrian.py (versi super cepat & stabil)
-------------------------------------------------
Fitur:
✅ Loop memantau halaman (via requests/BeautifulSoup)
✅ Jika form antrian terdeteksi → buka Chrome & isi otomatis
✅ Isi nama, KTP, nomor HP, centang dua checkbox, isi CAPTCHA (manual jika perlu), klik "Daftar"
✅ FAST_MODE benar-benar mempercepat semua proses input
"""

import time
import random
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# TARGET URL: 
# 2 . SETIABUDI 07:30 ✅
# https://www.antributikemas.com
# 4 . PULOGADUNG 07:30 ✅
# http://antrigrahadipta.com/
# 5 . TB SIMATUPANG 15:00 ✅
# https://antrisimatupang.com/
# 6 . BEKASI 07:00 :
# https://www.antributikbekasi.com/
# 7 . JUANDA 07:30 ✅
# https://www.antrijktjd5.com
# 8 . BOGOR 07:15 ✅
# https://antribgr1.com/
# 9 . PURI INDAH 07:30
# https://www.antrijktpr6.com
 
# DATA INPUT:
# Nama : DEWI AGUSTINA SUSANTI
# Nik : 3271025208960006
# No hp : 089608678980
# Nama : BERLINTAN JAYANTI 
# Nik : 3201016003910011
# No Hp : 082299560210
# Nama,: TUTUT WAHYUNI 
# Nik : 3275075403790021
# No hp : 081388344936
# Nama: TIARA
# NIK: 3275076408050001
# NO HP: 085945830366
# Nama : MUHAMMAD FAIZ RAMADHAN
# Nik : 3171051611030001
# No telp : 08111965944
# Nama: YENI MARLINA
# NIK: 0375074105880010
# NO HP: 082111516100

# ---------------- CONFIG ----------------
TARGET_URL = "http://127.0.0.1:8080/antribgr1.com/"
NAME = "MUHAMMAD FAIZ RAMADHAN"
KTP = "3171051611030001"
PHONE = "08111965944"

FAST_MODE = True            # True = super cepat, False = delay acak seperti manusia
HEADLESS = False            # False agar bisa isi CAPTCHA manual
POLL_INTERVAL = 10          # jeda antar pengecekan HTML (detik)
REQUEST_TIMEOUT = 10
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
# ----------------------------------------


def human_delay(min_s=0.05, max_s=0.25):
    """
    Delay antar aksi agar tampak natural.
    Jika FAST_MODE aktif → delay super kecil (nyaris instan).
    """
    if FAST_MODE:
        time.sleep(0.01)  # nyaris instan
    else:
        time.sleep(random.uniform(min_s, max_s))


def page_has_form(url: str) -> bool:
    """Cek HTML statis untuk mendeteksi elemen form target"""
    try:
        headers = {"User-Agent": USER_AGENT}
        resp = requests.get(url, timeout=REQUEST_TIMEOUT, headers=headers)
        if resp.status_code != 200:
            print(f"[i] HTTP {resp.status_code} saat meminta {url}")
            return False

        soup = BeautifulSoup(resp.text, "html.parser")
        if soup.find(id="name") or soup.find(id="ktp") or soup.find(id="phone_number"):
            return True
        return False
    except requests.RequestException as e:
        print(f"[!] Error requests: {e}")
        return False


def run_selenium_fill(url: str):
    """Buka Chrome, isi form, centang checkbox, isi captcha, klik tombol Daftar"""
    chrome_opts = Options()
    if HEADLESS:
        chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")
    chrome_opts.add_argument("--disable-blink-features=AutomationControlled")

    print("\n[i] Membuka Chrome (Selenium) untuk mengisi form...")
    driver = webdriver.Chrome(options=chrome_opts)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get(url)
        print("[i] Membuka halaman:", url)
        wait.until(EC.presence_of_element_located((By.ID, "name")))

        # ==== Isi data form ====
        print("[+] Mengisi Nama...")
        name_el = driver.find_element(By.ID, "name")
        name_el.clear()
        human_delay()
        name_el.send_keys(NAME)

        print("[+] Mengisi Nomor KTP...")
        ktp_el = driver.find_element(By.ID, "ktp")
        ktp_el.clear()
        human_delay()
        ktp_el.send_keys(KTP)

        print("[+] Mengisi Nomor HP...")
        phone_el = driver.find_element(By.ID, "phone_number")
        phone_el.clear()
        human_delay()
        phone_el.send_keys(PHONE)

        # ==== Centang checkbox ====
        print("[+] Menyetujui syarat dan ketentuan...")
        for cid in ["check", "check_2"]:
            try:
                checkbox = wait.until(EC.presence_of_element_located((By.ID, cid)))
                driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                    checkbox,
                )
                human_delay()
                # Coba klik biasa dulu
                try:
                    checkbox.click()
                except Exception:
                    # Kalau gagal (tertutup elemen lain), pakai JS click
                    driver.execute_script("arguments[0].click();", checkbox)
                human_delay()
                print(f"[✓] Checkbox {cid} dicentang.")
            except Exception as e:
                print(f"[!] Gagal mencentang {cid}: {e}")

        # ==== CAPTCHA ====
        try:
            captcha_box = driver.find_element(By.ID, "captcha-box")
            visible_text = captcha_box.text.strip()
            if visible_text:
                captcha_input = driver.find_element(By.ID, "captcha_input")
                captcha_input.clear()
                human_delay()
                captcha_input.send_keys(visible_text)
                print(f"[+] CAPTCHA diisi otomatis: {visible_text}")
            else:
                print("[!] CAPTCHA kosong (kemungkinan gambar/reCAPTCHA).")
                print("Silakan isi CAPTCHA manual di browser, lalu tekan ENTER di terminal.")
                input("Tekan ENTER setelah CAPTCHA selesai...")
        except Exception:
            print("[i] Tidak menemukan elemen CAPTCHA, lanjutkan...")

        # ==== Klik tombol Daftar ====
        print("[>] Mencoba klik tombol 'Daftar'...")
        daftar_btn = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[contains(text(), 'Daftar') or @type='submit']")
            )
        )
        driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", daftar_btn
        )
        human_delay()
        try:
            daftar_btn.click()
            print("[✓] Tombol 'Daftar' berhasil diklik.")
        except Exception:
            driver.execute_script("arguments[0].click();", daftar_btn)
            print("[✓] Klik via JavaScript berhasil.")

        # Tunggu hasil submit sebentar
        time.sleep(2 if FAST_MODE else 5)
        print(f"[i] Halaman setelah submit: {driver.current_url}")

    except Exception as e:
        print(f"[!] Error saat mengisi form: {e}")
    finally:
        print("[i] Menutup Chrome...")
        time.sleep(1 if FAST_MODE else 5)
        driver.quit()


def main():
    print("[i] Auto-fill watcher berjalan. Tekan Ctrl+C untuk berhenti.\n")
    while True:
        print(f"[i] Mengecek halaman: {TARGET_URL}")
        if page_has_form(TARGET_URL):
            print("[✓] Form antrian terdeteksi aktif. Membuka Selenium...\n")
            run_selenium_fill(TARGET_URL)
            break
        else:
            print(f"[i] Form belum aktif. Menunggu {POLL_INTERVAL} detik...\n")
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
