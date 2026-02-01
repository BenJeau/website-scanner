import json
import argparse

from src.scanner import scan_websites, create_profiles


if __name__ == "__main__":
    create_profiles()

    parser = argparse.ArgumentParser(description="Scrape websites using botasaurus.")
    parser.add_argument(
        "urls", nargs="*", help="One or more URLs to scrape (for CLI mode)."
    )

    args = parser.parse_args()
    results = scan_websites(args.urls)

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
