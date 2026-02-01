import os
import threading
import uuid
import json

from fastapi import FastAPI
import requests

from src.scanner import scan_websites, create_profiles

create_profiles()
app = FastAPI()


def scan_website_and_send_to_webhook(url: str, webhook_url: str | None, scan_id: str):
    os.makedirs("scans", exist_ok=True)
    file_path = f"scans/{scan_id}.json"
    with open(file_path, "w") as f:
        pass

    try:
        result = scan_websites([url])[0]
    except Exception as e:
        print(e)
        result = {"error": str(e), "original_url": url, "success": False}

    with open(file_path, "w") as f:
        json.dump(result, f, indent=2)

    if webhook_url:
        response = requests.post(webhook_url, json=result, timeout=5)
        response.raise_for_status()


@app.post("/api/v1/scan", status_code=202)
def scan_url(url: str, webhook_url: str | None = os.getenv("WEBHOOK_URL")):
    scan_id = uuid.uuid4().hex

    thread = threading.Thread(
        target=scan_website_and_send_to_webhook, args=(url, webhook_url, scan_id)
    )
    thread.daemon = True
    thread.start()

    return {
        "id": scan_id,
        "message": "Scan started",
        "url": url,
        "webhook": webhook_url,
    }


@app.get("/api/v1/scan/{id}")
def get_scan_result(id: str):
    file_path = f"scans/{id}.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            if os.path.getsize(file_path) == 0:
                return {"error": "Scan in progress", "id": id}

            return json.load(f)
    else:
        return {"error": "Scan not found", "id": id}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
