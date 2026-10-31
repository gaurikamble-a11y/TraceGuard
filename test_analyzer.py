
import unittest

from analyzer import analyze_event


class TestTraceGuardAnalyzer(unittest.TestCase):

    def setUp(self):
        self.event = {
            "url": "http://127.0.0.1:8001/",
            "scheme": "http",
            "status_code": 200,
            "response_headers": {
                "content-type": "text/plain"
            },
            "cookies": [
                {
                    "name": "demo_session",
                    "attributes": []
                }
            ],
        }

    def test_detects_unencrypted_http(self):
        findings = analyze_event(self.event)
        rules = [item["rule"] for item in findings]
        self.assertIn("Unencrypted HTTP", rules)

    def test_detects_missing_csp(self):
        findings = analyze_event(self.event)
        rules = [item["rule"] for item in findings]
        self.assertIn("Missing Content-Security-Policy", rules)

    def test_detects_missing_content_type_options(self):
        findings = analyze_event(self.event)
        rules = [item["rule"] for item in findings]
        self.assertIn("Missing X-Content-Type-Options", rules)

    def test_detects_cookie_missing_secure(self):
        findings = analyze_event(self.event)
        rules = [item["rule"] for item in findings]
        self.assertIn("Cookie missing Secure", rules)

    def test_detects_cookie_missing_httponly(self):
        findings = analyze_event(self.event)
        rules = [item["rule"] for item in findings]
        self.assertIn("Cookie missing HttpOnly", rules)

    def test_detects_cookie_missing_samesite(self):
        findings = analyze_event(self.event)
        rules = [item["rule"] for item in findings]
        self.assertIn("Cookie missing SameSite", rules)

    def test_secure_cookie_does_not_trigger_secure_warning(self):
        event = {
            **self.event,
            "cookies": [{
                "name": "safe_session",
                "attributes": [
                    "secure", "httponly", "samesite=lax"
                ]
            }],
        }

        findings = analyze_event(event)
        rules = [item["rule"] for item in findings]

        self.assertNotIn("Cookie missing Secure", rules)
        self.assertNotIn("Cookie missing HttpOnly", rules)
        self.assertNotIn("Cookie missing SameSite", rules)


if __name__ == "__main__":
    unittest.main(verbosity=2)
