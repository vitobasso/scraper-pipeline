import json
import re
from asyncio import wait_for
from contextlib import asynccontextmanager
from typing import Literal

from playwright._impl._errors import TimeoutError, Error as PlaywrightError
from playwright.async_api import async_playwright, ProxySettings, ViewportSize

from src.config import use_proxies

timeout_millis = 60000
timeout_secs = 60


@asynccontextmanager
async def new_page(proxy: str):
    async with async_playwright() as playwright:
        proxy_settings: ProxySettings = {'server': f'{proxy}'}

        browser = await playwright.chromium.launch(
            headless=True,
            proxy=proxy_settings if use_proxies else None,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox', # loosen this security feature to avoid incompatibility with kernel
                '--disable-gpu', # avoid hanging if chrome attempts graphic acceleration, but it's not available in VM
                # '--disable-dev-shm-usage', # avoid /dev/shm if short on RAM. use /tmp, i.e. disk, instead
                # '--disable-web-security', # bypass CORS
                # '--disable-extensions'
            ]
        )

        viewport: ViewportSize = {'width': 1280, 'height': 720}
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            viewport=viewport,
            ignore_https_errors=True,  # avoids ERR_CERT_AUTHORITY_INVALID, risks getting data tampered by MIM
            bypass_csp=True,
        )

        await context.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/'
        })

        page = await context.new_page()

        try:
            yield page
        except Exception:
            raise
        finally:
            await browser.close()


@asynccontextmanager
async def page_goto(proxy: str, url: str,
                    wait_until: Literal['commit', 'domcontentloaded', 'load', 'networkidle'] = 'domcontentloaded'):
    async with new_page(proxy) as page:
        await page.goto(url, timeout=timeout_millis, wait_until=wait_until)
        yield page


async def click(page, selector: str, button_text: str = '', timeout=None):
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


async def expect_json_response(file_path: str, page, url: str, condition):
    async with page.expect_response(condition, timeout=timeout_millis) as response_info:
        await page.goto(url, timeout=timeout_millis, wait_until='domcontentloaded')
    response = await wait_for(response_info.value, timeout_secs)
    data = await wait_for(response.json(), timeout_secs)
    with open(file_path, 'w') as f:
        json.dump(data, f)


def common_ancestor(page, texts: list[str]):
    children = ' and '.join([_xpath_contains(text) for text in texts])
    return page.locator(f"""xpath=//*[{children}]""").last


def _xpath_contains(text: str):
    return f".//text()[contains(., '{text}')]"


def error_name(e: Exception):
    if isinstance(e, TimeoutError):
        return type(e).__name__
    if isinstance(e, PlaywrightError):
        match = re.search(r'ERR_\w+', str(e))
        return match.group(0) if match else str(e)
    else:
        return str(e)
