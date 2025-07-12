# website scanner

a small python script using [botasaurus](https://github.com/omkarcloud/botasaurus/) as a proof of concept to scan websites using a non-headless chrome browser and bypass many anti-bot measures. (headless browsers are _almost always_ as bots by websites)

## features

- bypasses cloudflare
- randomly sets http referer (current page, google, bing, yahoo, duckduckgo, or none)
- randomly creates and sets a chrome profile
- simulates human cursor movements
- adds a random delay between requests
- parallelizes requests
- caches requests
- captures screenshots
- reuses chrome driver instances
- retries requests on failure
- collects data from the website
  - title
  - destination url
  - html response
  - parsed text response
  - cookies
  - local storage
  - ip address of the host
  - screenshot of the whole page in base64 format
  - all requests made by the browser while visiting the website

## how to run

install [uv](https://docs.astral.sh/uv/) and run the script with the urls you want to scrape as arguments.

```bash
uv run main.py https://jeaurond.dev https://google.com
```

to use caching, retries, parallelization, etc. set the `ENV` environment variable to `PROD`, e.g.

```bash
ENV=PROD uv run main.py https://jeaurond.dev https://google.com
```

## how to run as a server

assuming you have a server already accepting post requests (or if you do not have one, feel free to try it by running `uv run examples/webhook_server.py`), you can run the script as a server by passing the `--server` flag and the webhook url as an argument.

```bash
uv run main.py --server --webhook http://localhost:4567/webhook
```

this will start a server on `http://localhost:8080/` and will accept get requests to `http://localhost:8080/api/v1/scan?url=<URL>`.

the script will then scan the website and send the results to the webhook url via post in a json format.

## license

project is licensed under the [MIT license](LICENSE)
