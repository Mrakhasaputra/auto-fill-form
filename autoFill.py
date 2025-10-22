"""
auto_fill_antrian.py
---------------------------------
Selenium bot untuk mengisi otomatis form "Daftar Antrian"
di https://antribgr1.com (Butik Emas LM ANTAM Bogor).

Catatan:
- Bot ini **tidak mem-bypass reCAPTCHA** (akan pause agar kamu isi manual).
- Menggunakan Chrome yang sudah terpasang di sistem kamu (tanpa webdriver-manager).
- Pastikan Google Chrome dan chromedriver versi sama.
"""

import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ---------------- CONFIG ----------------
TARGET_URL = "http://127.0.0.1:5500/antrigrahadipta.com/index.html"  # halaman daftar antrian
NAME = "Nama Contoh"
KTP = "1234567890123456"
PHONE = "081234567890"
FAST_MODE = True          # True = cepat, False = delay acak seperti manusia
HEADLESS = False          # False agar bisa isi CAPTCHA manual
# ----------------------------------------


def human_delay(min_s=0.05, max_s=0.25):
    """Delay antar aksi agar tidak terlalu cepat"""
    if FAST_MODE:
        time.sleep(min_s)
    else:
        time.sleep(random.uniform(min_s, max_s))


def main():
    # Setup Chrome
    chrome_opts = Options()
    if HEADLESS:
        chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")
    chrome_opts.add_argument("--disable-blink-features=AutomationControlled")

    print("[i] Membuka Chrome...")
    driver = webdriver.Chrome(options=chrome_opts)
    wait = WebDriverWait(driver, 15)

    try:
        # Buka halaman utama
        print("[i] Membuka halaman:", TARGET_URL)
        driver.get(TARGET_URL)

        # Tunggu elemen nama muncul
        wait.until(EC.presence_of_element_located((By.ID, "name")))

        # Cek apakah ada reCAPTCHA
        try:
            grecaptcha_present = driver.execute_script("return (typeof window.grecaptcha !== 'undefined');")
        except Exception:
            grecaptcha_present = False

        # Ambil elemen form
        name_el = driver.find_element(By.ID, "name")
        ktp_el = driver.find_element(By.ID, "ktp")
        phone_el = driver.find_element(By.ID, "phone_number")
        check1 = driver.find_element(By.ID, "check")
        check2 = driver.find_element(By.ID, "check_2")

        # Isi form
        print("[+] Mengisi Nama...")
        name_el.clear(); human_delay()
        name_el.send_keys(NAME); human_delay()

        print("[+] Mengisi KTP...")
        ktp_el.clear(); human_delay()
        ktp_el.send_keys(KTP); human_delay()

        print("[+] Mengisi Nomor HP...")
        phone_el.clear(); human_delay()
        phone_el.send_keys(PHONE); human_delay()

        # Centang checkbox
        if not check1.is_selected():
            check1.click(); human_delay()
        if not check2.is_selected():
            check2.click(); human_delay()

        # Isi captcha jika ada teks statis
        try:
            captcha_box = driver.find_element(By.ID, "captcha-box")
            visible_text = captcha_box.text.strip()
            captcha_input = driver.find_element(By.ID, "captcha_input")
            captcha_input.clear(); human_delay()
            captcha_input.send_keys(visible_text)
            print(f"[+] Captcha diisi otomatis: {visible_text}")
        except Exception:
            print("[i] Tidak menemukan captcha statis, lanjutkan manual jika perlu.")

        # Jika reCAPTCHA terdeteksi, tunggu manual
        if grecaptcha_present:
            print("\n[!] reCAPTCHA terdeteksi!")
            print("Silakan isi reCAPTCHA di browser, lalu tekan ENTER di terminal untuk lanjut submit.")
            input("Tekan ENTER setelah reCAPTCHA selesai...")

        # Submit form
        # Submit form dengan scroll dan JS fallback
        print("[>] Mencoba klik tombol Submit...")
        submit_btn = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']")))

        # Scroll tombol ke tampilan agar terlihat
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_btn)
        time.sleep(1)

        try:
            # Coba klik normal dulu
            submit_btn.click()
        except Exception:
            # Kalau gagal karena terhalang, klik via JS
            print("[!] Tombol submit terhalang, klik via JavaScript...")
            driver.execute_script("arguments[0].click();", submit_btn)


        # Tunggu beberapa detik untuk lihat hasil
        print("[i] Form submitted. Tunggu respon halaman...")
        time.sleep(3)

    except Exception as e:
        print("[!] Terjadi error:", e)
    finally:
        print("[i] Menutup Chrome dalam 5 detik...")
        time.sleep(5)
        driver.quit()


if __name__ == "__main__":
    main()
