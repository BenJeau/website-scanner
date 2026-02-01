import random
import os

from botasaurus.browser import browser, Driver, cdp
from botasaurus.profiles import Profiles
from botasaurus.ip_utils import IPUtils
from chrome_extension_python import Extension
from faker import Faker


IS_PROD = os.environ.get("ENV") == "PROD"

profiles = []


def create_profiles():
    global profiles

    fake = Faker()
    for _ in range(20):
        profile = {
            "name": fake.name(),
            "age": random.randint(18, 60),
            "email": fake.email(),
            "address": fake.address(),
            "phone": fake.phone_number(),
        }
        username = fake.user_name()
        Profiles.set_profile(username, profile)
        profiles.append(username)


def get_screenshot(driver: Driver) -> str:
    return driver.run_cdp_command(
        cdp.page.capture_screenshot(
            format_="png", capture_beyond_viewport=True, optimize_for_speed=True
        )
    )


def navigate_to_url(driver: Driver, url: str) -> str | None:
    referer = None
    if random.random() < 0.5:
        referer = "current_page"
        driver.get_via_this_page(url, bypass_cloudflare=True)
    elif random.random() < 0.6:
        referer = "google"
        driver.google_get(url, bypass_cloudflare=True)
    elif random.random() < 0.7:
        referer = "bing"
        driver.get_via(url, referer="https://www.bing.com", bypass_cloudflare=True)
    elif random.random() < 0.8:
        referer = "yahoo"
        driver.get_via(url, referer="https://www.yahoo.com", bypass_cloudflare=True)
    elif random.random() < 0.9:
        referer = "duckduckgo"
        driver.get_via(
            url, referer="https://www.duckduckgo.com", bypass_cloudflare=True
        )
    else:
        driver.get(url, bypass_cloudflare=True)

    return referer


@browser(
    # TODO: maybe add extensions to make it more human like
    extensions=[
        Extension(
            "https://chromewebstore.google.com/detail/wappalyzer-technology-pro/gppongmhjkpfnbhagpmjfkannfbllamg"
        ),
        Extension(
            "https://chromewebstore.google.com/detail/ublock-origin-lite/ddkjiahejlhfcafbddmgiahcphecmpfh"
        ),
    ],
    profile=lambda data: random.choice(profiles),
    reuse_driver=True,
    tiny_profile=True,
    output=None,
    remove_default_browser_check_argument=True,
    max_retry=5 if IS_PROD else 1,
    cache=True if IS_PROD else False,
    parallel=5 if IS_PROD else 1,
    close_on_crash=IS_PROD,
    raise_exception=IS_PROD,
    create_error_logs=not IS_PROD,
)
def scan_websites(driver: Driver, url: str):
    human_mode = False
    if random.random() < 0.5:
        human_mode = True
        driver.enable_human_mode()

    def after_response_handler(
        _request_id: str,
        response: cdp.network.Response,
        _event: cdp.network.ResponseReceived,
    ):
        if response.url.startswith("chrome"):
            return
        driver.responses.append(response.to_json())

    driver.after_response_received(after_response_handler)
    referer = navigate_to_url(driver, url)

    return {
        "original_url": url,
        "final_url": driver.current_url,
        "title": driver.title,
        "cookies": driver.get_cookies(),
        "local_storage": driver.get_local_storage(),
        "human_mode": human_mode,
        "referer": referer,
        "ip": IPUtils.get_ip_info(),
        "html": driver.page_html,
        "text": driver.page_text,
        "screenshot": get_screenshot(driver),
        "requests": driver.responses,
    }
