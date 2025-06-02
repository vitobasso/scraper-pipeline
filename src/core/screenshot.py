from playwright.async_api import async_playwright, ProxySettings
from src.core.config import config

load_timeout = config.get('screenshot.browser.load_timeout')
after_load_timeout = config.get('screenshot.browser.after_load_timeout')

async def screenshot(url: str, path: str, proxy: str):
    async with async_playwright() as playwright:
        proxy_settings: ProxySettings = {'server': f'http://{proxy}'}

        # Launch browser with anti-detection options
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

        # Create context with custom user agent and viewport
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            viewport={'width': 1280, 'height': 720},
            # Some sites check for webdriver property
            bypass_csp=True
        )

        # Optionally set extra headers
        await context.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/'
        })

        page = await context.new_page()

        try:
            # Navigate with longer timeout and wait strategy
            await page.goto(
                url,
                timeout=load_timeout,
                wait_until='load'
            )

            # Wait a bit to let page load completely
            await page.wait_for_timeout(after_load_timeout)

            # Take screenshot
            await page.screenshot(
                path=path,
                full_page=True,
                animations='disabled'  # Disable animations for cleaner screenshot
            )

        finally:
            await browser.close()
