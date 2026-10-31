
import json
from datetime import datetime, timezone
from http.cookies import SimpleCookie
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from analyzer import analyze_event

LOG_FILE = Path(__file__).with_name("traffic.jsonl")


def safe_url(url):
    """Save the URL without query parameters or fragments."""
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def extract_cookie_metadata(response):
    """Extract cookie names and attributes without saving cookie values."""
    cookies = []

    # get_all handles multiple Set-Cookie headers where supported.
    try:
        set_cookie_headers = response.headers.get_all("set-cookie")
    except AttributeError:
        set_cookie_headers = []

    if not set_cookie_headers:
        single = response.headers.get("set-cookie")
        if single:
            set_cookie_headers = [single]

    for header in set_cookie_headers:
        parsed = SimpleCookie()

        try:
            parsed.load(header)
        except Exception:
            continue

        for name, morsel in parsed.items():
            attributes = []

            if morsel["secure"]:
                attributes.append("secure")
            if morsel["httponly"]:
                attributes.append("httponly")
            if morsel["samesite"]:
                attributes.append(f"samesite={morsel['samesite'].lower()}")

            cookies.append({
                "name": name,
                "attributes": attributes,
            })

    return cookies


class TraceGuardAddon:
    def response(self, flow):
        request = flow.request
        response = flow.response

        request_headers = {
            key.lower(): value
            for key, value in request.headers.items()
            if key.lower() in {"host", "user-agent", "content-type"}
        }

        response_headers = {
            key.lower(): value
            for key, value in response.headers.items()
            if key.lower() in {
                "content-type",
                "content-security-policy",
                "x-content-type-options",
                "strict-transport-security",
            }
        }

        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "host": request.pretty_host,
            "url": safe_url(request.pretty_url),
            "method": request.method,
            "scheme": request.scheme,
            "status_code": response.status_code,
            "response_time_ms": round(
                (response.timestamp_end - request.timestamp_start) * 1000,
                2,
            ) if response.timestamp_end and request.timestamp_start else None,
            "request_headers": request_headers,
            "response_headers": response_headers,
            "cookies": extract_cookie_metadata(response),
        }

        event["findings"] = analyze_event(event)

        with LOG_FILE.open("a", encoding="utf-8") as file:
            file.write(json.dumps(event) + "\n")


addons = [TraceGuardAddon()]
