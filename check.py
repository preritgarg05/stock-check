import asyncio
from playwright.async_api import async_playwright


PINCODE = "560102"


import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

products = {"Milkshake": "https://shop.amul.com/en/product/amul-kool-protein-milkshake-or-chocolate-180-ml-or-pack-of-8",
 "Rose Lassi": "https://shop.amul.com/en/product/amul-high-protein-rose-lassi-200-ml-or-pack-of-30",
 "Normal Lassi": "https://shop.amul.com/en/product/amul-high-protein-plain-lassi-200-ml-or-pack-of-30"}


import requests

def send_telegram(product):
    message = f"🚀 {product} is IN STOCK!"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(url, data=payload)

from datetime import datetime
from zoneinfo import ZoneInfo

async def check_stock():
    async with async_playwright() as p:
        for product, url in products.items():
            
            current_minute = datetime.now(ZoneInfo("Asia/Kolkata")).minute

            if product == "Milkshake" and not (35 <= current_minute <= 42):
                print(f"Skipping {product} — outside time window")
                continue

            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                ]
            )

            page = await browser.new_page()

            await page.goto(url, timeout=60000)
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(3000)

            try:
                box = page.locator("#search")
                await box.wait_for(timeout=2000)
                await box.fill(PINCODE)
                await page.wait_for_timeout(3000)
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(3000)
            except:
                print("Pincode already set")


            await page.wait_for_selector("a.add-to-cart", timeout=30000)
            button = page.locator("a.add-to-cart").first


            disabled_attr = await button.get_attribute("disabled")
            classes = await button.get_attribute("class") or ""

            is_disabled = (
                disabled_attr == "true" or
                "disabled" in classes
            )

            if is_disabled:
                print(f"{product} is still Out of Stock ❌")
            else:
                print(f"{product} IN STOCK ✅")
                send_telegram(product)

            await browser.close()


import time

for i in range(2):
    asyncio.run(check_stock())
    if i == 1:
        break
    time.sleep(60)
    

