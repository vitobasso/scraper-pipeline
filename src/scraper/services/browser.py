import asyncio
import re
from asyncio import wait_for
from collections.abc import Callable, Coroutine
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal
from urllib.parse import urljoin

from playwright.async_api import Error, Page, ProxySettings, TimeoutError, ViewportSize, async_playwright

from src.common import config

timeout_millis = 60000
timeout_secs = timeout_millis // 1000
WaitUntil = Literal["commit", "domcontentloaded", "load", "networkidle"]


@asynccontextmanager
async def new_page(proxy: str):
    async with async_playwright() as playwright:
        proxy_settings: ProxySettings | None = {"server": f"{proxy}"} if proxy else None

        browser = await playwright.chromium.launch(
            channel="chromium",  # headless mode more realistic. might use more RAM/CPU.
            headless=True,
            proxy=proxy_settings,
            args=[
                "--disable-blink-features=AutomationControlled",  # anti-bot detection evasion
                "--no-sandbox",  # saves RAM and CPU, avoids permission issues, loosens security
                "--disable-gpu",  # saves RAM
                "--disable-software-rasterizer",  # saves RAM, avoid cpu-based renderer when gpu is disabled
                "--no-default-browser-check",  # would save RAM. probably redundant in headless chrome
                "--no-first-run",  # would save RAM. probably redundant in headless chrome
                "--disable-extensions",  # would save RAM. probably redundant in headless chrome
                "--mute-audio",
                # "--disable-background-timer-throttling",  # prevent throttling of background tabs
                # "--disable-backgrounding-occluded-windows", # prevent throttling of background tabs
                # "--disable-dev-shm-usage",  # avoid /dev/shm if short on RAM. use /tmp, i.e. disk, instead
                # "--disable-web-security",  # bypass CORS
            ],
        )

        viewport: ViewportSize = {"width": 1280, "height": 720}
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 "
                "Safari/537.36"
            ),
            viewport=viewport,
            ignore_https_errors=not config.enforce_https,
            bypass_csp=True,
        )

        await context.set_extra_http_headers(
            {
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.google.com/",
            }
        )

        await context.route("**/*", _prune_requests)

        page = await context.new_page()

        try:
            yield page
        finally:
            try:
                try:
                    # give a brief moment for pending tasks (downloads/responses) to resolve
                    await page.wait_for_load_state("networkidle", timeout=1000)
                except Exception:
                    pass
                await context.close()
            finally:
                await browser.close()


async def _prune_requests(route):
    if route.request.resource_type in ["image", "media", "font"]:
        await route.abort()
    else:
        await route.continue_()


@asynccontextmanager
async def page_goto(proxy: str, url: str, wait_until: WaitUntil = "domcontentloaded"):
    async with new_page(proxy) as page:
        await page.goto(url, timeout=timeout_millis, wait_until=wait_until)
        yield page


async def goto(page, url: str, wait_until: WaitUntil = "domcontentloaded"):
    await page.goto(url, timeout=timeout_millis, wait_until=wait_until)


async def click(page, selector: str, button_text: str = "", timeout=None):
    button = page.locator(selector, has_text=button_text)
    await button.wait_for(state="visible", timeout=timeout)
    await button.click()


async def click_download(file_path: Path, page, selector: str, button_text: str):
    button = page.locator(selector, has_text=button_text)
    await button.wait_for(state="visible")
    async with page.expect_download() as download_info:
        await button.click()
    download = await download_info.value
    await download.save_as(file_path)


async def expect_json_response(page, url: str, condition):
    async with page.expect_response(condition, timeout=timeout_millis) as response_info:
        await page.goto(url, timeout=timeout_millis, wait_until="domcontentloaded")
    response = await wait_for(response_info.value, timeout_secs)
    data = await wait_for(response.json(), timeout_secs)
    return data


def common_ancestor(page: Page, scope_selectors: list[str]):
    children = " and ".join([_xpath_contains(text) for text in scope_selectors])
    return page.locator(f"""xpath=//*[{children}]""").last


def _xpath_contains(text: str) -> str:
    return f".//text()[contains(., '{text}')]"


def error_name(e: Exception) -> str:
    if isinstance(e, TimeoutError):
        return type(e).__name__
    if isinstance(e, Error):
        match = re.search(r"ERR_\w+", str(e))
        return match.group(0) if match else str(e)
    else:
        return str(e)


async def download_bytes(page, url: str) -> bytes:
    resp = await page.context.request.get(url)
    if not resp.ok:
        raise RuntimeError(f"Failed to fetch: {url}, status={resp.status}")
    return await resp.body()


async def find_url_contains(page, base_url: str, substring: str) -> str:
    """Find absolute URL whose href contains the given substring (case-insensitive)."""
    sub_l = substring.lower()
    return await find_url(page, base_url, href_predicate=lambda h: bool(h) and sub_l in h.lower())


async def find_url_regex(page, base_url: str, pattern: str | re.Pattern) -> str:
    """Find absolute URL whose href matches the provided regex pattern (case-insensitive if str)."""
    rx = re.compile(pattern, re.IGNORECASE) if isinstance(pattern, str) else pattern
    return await find_url(page, base_url, href_predicate=lambda h: bool(h) and bool(rx.search(h)))


async def find_url(page, base_url: str, href_predicate: Callable[[str], bool]) -> str:
    """Find absolute URL that matches href_predicate by scanning DOM and, if needed, HTML.
    - href_predicate: receives the raw href string and returns True if it matches.
    """
    try:
        await page.wait_for_load_state("load", timeout=timeout_millis)
    except Exception:
        pass
    href = await _scan_dom_for_href(page, href_predicate)
    if not href:
        href = await _scan_html_for_href(page, base_url, href_predicate)
    if not href:
        raise RuntimeError("Could not find matching link on page via DOM or HTML fetch")
    return urljoin(base_url, href)


async def _scan_dom_for_href(page, href_predicate: Callable[[str], bool]) -> str | None:
    try:
        hrefs = await page.evaluate(
            """
            (() => Array.from(document.querySelectorAll('a'))
              .map(a => a.getAttribute('href'))
              .filter(Boolean))()
            """
        )
        if not hrefs:
            return None
        for h in hrefs:
            try:
                if href_predicate(h):
                    return h
            except Exception:
                continue
        return None
    except Exception:
        return None


async def _scan_html_for_href(page, url: str, href_predicate: Callable[[str], bool]) -> str | None:
    try:
        r = await page.context.request.get(url)
        if not r.ok:
            return None
        html_text = await r.text()
        hrefs = _extract_hrefs(html_text)
        for h in hrefs:
            try:
                if href_predicate(h):
                    return h
            except Exception:
                continue
        return None
    except Exception:
        return None


def _extract_hrefs(html_text: str) -> list[str]:
    # Capture href values in single or double quotes, ignoring spaces and '>'
    return re.findall(r"href=[\"']([^\"'\s>]+)[\"']", html_text, flags=re.IGNORECASE)


async def expect_either(page: Page, f1: Callable[[Page], Coroutine], f2: Callable[[Page], Coroutine]):
    tasks = [
        asyncio.create_task(f1(page)),
        asyncio.create_task(f2(page)),
    ]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()
    return done.pop().result()


async def wait_idle(page: Page):
    await page.wait_for_load_state("networkidle", timeout=timeout_millis)
