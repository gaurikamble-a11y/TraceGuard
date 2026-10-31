
from http.server import BaseHTTPRequestHandler, HTTPServer


class TestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header(
            "Set-Cookie",
            "demo_session=synthetic_test_value; Path=/"
        )
        self.end_headers()

        self.wfile.write(
            b"TraceGuard controlled security test endpoint."
        )

    def log_message(self, format, *args):
        print("[TEST SERVER]", format % args)


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8001), TestHandler)
    print("TraceGuard test server running at http://127.0.0.1:8001")
    server.serve_forever()
