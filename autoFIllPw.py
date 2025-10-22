# pip install playwright
# playwright install
import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headful recommended if captcha
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("http://127.0.0.1:5500/antribgr1.com/index.html")
        await page.fill("#name", "Nama Contoh")
        await page.fill("#ktp", "1234567890123456")
        await page.fill("#phone_number", "081234567890")
        await page.check("#check")
        await page.check("#check_2")
        # isi captcha statis jika ada
        try:
            text = await page.locator("#captcha-box").inner_text(timeout=2000)
            await page.fill("#captcha_input", text.strip())
        except:
            pass
        # # detect grecaptcha and pause for manual
        # gre = await page.evaluate("()=>typeof window.grecaptcha !== 'undefined'")
        # if gre:
        #     print("Selesaikan reCAPTCHA di browser, lalu tekan Enter di terminal...")
        #     input()
        await page.click("button[type=submit]")
        await asyncio.sleep(3)
        await browser.close()

asyncio.run(run())
