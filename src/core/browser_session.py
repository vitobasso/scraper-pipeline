import re
from playwright._impl._errors import TimeoutError, Error as PlaywrightError
from playwright.async_api import async_playwright, ProxySettings, ViewportSize
from typing import Literal
from contextlib import asynccontextmanager

load_timeout = 60000

@asynccontextmanager
async def browser_page(proxy: str, url: str,
                  wait_until: Literal['commit', 'domcontentloaded', 'load', 'networkidle'] = 'domcontentloaded'):
    async with async_playwright() as playwright:
        proxy_settings: ProxySettings = {'server': f'{proxy}'}

        browser = await playwright.chromium.launch(
            headless=True,
            proxy=proxy_settings,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                # '--disable-dev-shm-usage',
                # '--disable-web-security',
                # '--disable-extensions'
            ]
        )

        viewport:ViewportSize = {'width': 1280, 'height': 720}
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            viewport=viewport,
            ignore_https_errors=True, # avoids ERR_CERT_AUTHORITY_INVALID, risks getting data tampered by MIM
            bypass_csp=True,
        )

        await context.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/'
        })

        page = await context.new_page()

        try:
            await page.goto(url, timeout=load_timeout, wait_until=wait_until)
            yield page
        except Exception:
            raise
        finally:
            await browser.close()


async def click(page, selector: str, button_text: str = '', timeout = None):
    button = page.locator(selector, has_text=button_text)
    await button.wait_for(state="visible", timeout=timeout)
    await button.click()

async def click_download(file_path: str, page, selector: str, button_text: str):
    button = page.locator(selector, has_text=button_text)
    await button.wait_for(state="visible")
    async with page.expect_download() as download_info:
        await button.click()
    download = await download_info.value
    await download.save_as(file_path)

def error_type(e: Exception):
    if isinstance(e, TimeoutError):
        return type(e).__name__
    if isinstance(e, PlaywrightError):
        match = re.search(r'ERR_\w+', str(e))
        return match.group(0) if match else str(e)
    else:
        return str(e)
