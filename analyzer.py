
from urllib.parse import urlsplit


def make_finding(rule_id, rule, severity, evidence, recommendation):
    return {
        "rule_id": rule_id,
        "rule": rule,
        "severity": severity,
        "evidence": evidence,
        "recommendation": recommendation,
    }


def analyze_event(event):
    """Evaluate one captured flow using transparent security rules."""
    findings = []

    url = event.get("url", "")
    scheme = (event.get("scheme") or urlsplit(url).scheme).lower()

    headers = {
        str(key).lower(): str(value)
        for key, value in event.get("response_headers", {}).items()
    }

    status_code = event.get("status_code")

    # Rule 1: Cleartext HTTP
    if scheme == "http":
        findings.append(make_finding(
            "TG-001",
            "Unencrypted HTTP",
            "High",
            "The request used HTTP rather than HTTPS.",
            "Use HTTPS to protect data in transit. Confirm whether "
            "cleartext access is expected in this test environment.",
        ))

    # Analyze response headers only when a response exists.
    if status_code is not None:
        # Rule 2: Content Security Policy
        if "content-security-policy" not in headers:
            findings.append(make_finding(
                "TG-002",
                "Missing Content-Security-Policy",
                "Low",
                "The response did not include a Content-Security-Policy header.",
                "Assess whether a suitable Content Security Policy "
                "is appropriate for this application.",
            ))

        # Rule 3: MIME sniffing protection
        if "x-content-type-options" not in headers:
            findings.append(make_finding(
                "TG-003",
                "Missing X-Content-Type-Options",
                "Low",
                "The response did not include X-Content-Type-Options.",
                "Consider setting X-Content-Type-Options: nosniff.",
            ))

        # Rule 4: HTTPS transport policy
        if scheme == "https" and "strict-transport-security" not in headers:
            findings.append(make_finding(
                "TG-004",
                "Missing HSTS header",
                "Low",
                "The HTTPS response did not include Strict-Transport-Security.",
                "Assess whether an appropriate HSTS policy is suitable "
                "for this host and its deployment.",
            ))

        # Rule 5: Cookie attributes
        # monitor.py must provide cookie metadata separately to use this rule.
        cookies = event.get("cookies", [])

        for index, cookie in enumerate(cookies, start=1):
            name = cookie.get("name", f"Cookie {index}")
            attributes = {
                str(attribute).lower()
                for attribute in cookie.get("attributes", [])
            }

            if "secure" not in attributes:
                findings.append(make_finding(
                    "TG-005",
                    "Cookie missing Secure",
                    "Medium",
                    f"{name} does not include the Secure attribute.",
                    "For cookies that should only travel over HTTPS, "
                    "set the Secure attribute.",
                ))

            if "httponly" not in attributes:
                findings.append(make_finding(
                    "TG-006",
                    "Cookie missing HttpOnly",
                    "Low",
                    f"{name} does not include the HttpOnly attribute.",
                    "Set HttpOnly for cookies that do not need to be "
                    "read by client-side JavaScript.",
                ))

            if not any(
                attribute.startswith("samesite=")
                for attribute in attributes
            ):
                findings.append(make_finding(
                    "TG-007",
                    "Cookie missing SameSite",
                    "Low",
                    f"{name} does not specify SameSite.",
                    "Choose an appropriate SameSite policy for the "
                    "cookie's purpose and authentication flow.",
                ))

    return findings

