import tempfile
import os
import base64
import json
import random
import argparse
import threading
import requests
from flask import Flask, request, jsonify

from botasaurus.browser import browser, Driver, cdp
from botasaurus.profiles import Profiles
from botasaurus.ip_utils import IPUtils
from faker import Faker

IS_PROD = os.environ.get("ENV") == "PROD"

profiles = []
app = Flask(__name__)


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
    tmp_path = tempfile.mkdtemp()
    screenshot_path = os.path.join(tmp_path, "screenshot.png")
    driver.save_screenshot(screenshot_path)
    screenshot = base64.b64encode(open(screenshot_path, "rb").read()).decode("utf-8")
    return screenshot


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
    extensions=[],
    profile=lambda data: random.choice(profiles),
    reuse_driver=True,
    max_retry=5 if IS_PROD else 1,
    tiny_profile=True,
    cache=True if IS_PROD else False,
    parallel=5 if IS_PROD else 1,
    close_on_crash=IS_PROD,
    raise_exception=IS_PROD,
    create_error_logs=not IS_PROD,
    output=None,
    remove_default_browser_check_argument=True,
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
    driver.short_random_sleep()

    return {
        "original_url": url,
        "final_url": driver.current_url,
        "title": driver.title,
        "chrome_profile": driver.profile,
        "cookies": driver.get_cookies_dict(),
        "local_storage": driver.get_local_storage(),
        "human_mode": human_mode,
        "referer": referer,
        "ip": IPUtils.get_ip_info(),
        "html": driver.page_html,
        "text": driver.page_text,
        "screenshot": get_screenshot(driver),
        "requests": driver.responses,
    }


def scan_website_and_send_to_webhook(url: str, webhook_url: str):
    try:
        result = scan_websites(url)
    except Exception as e:
        result = {"error": str(e), "original_url": url, "success": False}
    response = requests.post(webhook_url, json=result, timeout=5)
    response.raise_for_status()


@app.route("/api/v1/scan", methods=["GET"])
def scan_endpoint():
    """API endpoint to scan a URL"""
    url = request.args.get("url")

    if not url:
        return jsonify({"error": "url parameter is required"}), 400

    webhook_url = app.config.get("WEBHOOK_URL")

    thread = threading.Thread(
        target=scan_website_and_send_to_webhook, args=(url, webhook_url)
    )
    thread.daemon = True
    thread.start()

    return (
        jsonify(
            {
                "message": "Scan started",
                "url": url,
                "webhook": webhook_url,
            }
        ),
        202,
    )


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    create_profiles()

    parser = argparse.ArgumentParser(description="Scrape websites using botasaurus.")
    parser.add_argument(
        "urls", nargs="*", help="One or more URLs to scrape (for CLI mode)."
    )
    parser.add_argument(
        "--server", action="store_true", help="Run as a server instead of CLI mode"
    )
    parser.add_argument(
        "--webhook",
        type=str,
        help="Webhook URL to call with scan results (for CLI mode)",
    )
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="Server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="Server port (default: 8080)"
    )

    args = parser.parse_args()

    if args.server:
        if not args.webhook:
            parser.error("webhook is required when running in server mode")

        print(f"Starting server on {args.host}:{args.port}")
        print(f"Scan endpoint: http://{args.host}:{args.port}/api/v1/scan?url=<URL>")
        app.config["WEBHOOK_URL"] = args.webhook
        app.run(host=args.host, port=args.port, debug=not IS_PROD)
    else:
        print("Running in CLI mode")
        results = scan_websites(args.urls)

        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)
