import fcntl
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlsplit


DATA_FILE = Path("/data/counter.txt")
SERVICE_NAME = os.getenv("SERVICE_NAME") or "backend"


def read_counter():
    try:
        return int(DATA_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return 0


def increment_counter():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    # Обе реплики блокируют один и тот же файл в общей папке.
    with DATA_FILE.with_suffix(".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        value = read_counter() + 1
        # Читатель увидит либо прежнее число, либо полностью записанное новое.
        temporary = DATA_FILE.with_suffix(".tmp")
        temporary.write_text(f"{value}\n", encoding="utf-8")
        temporary.replace(DATA_FILE)
        return value


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, data):
        body = json.dumps({"service": SERVICE_NAME, **data}).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def handle_counter(self, operation):
        try:
            value = operation()
        except (OSError, ValueError) as error:
            self.send_json(500, {"error": str(error)})
            return
        self.send_json(200, {"counter": value})

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/health":
            self.send_json(200, {"status": "ok"})
        elif path == "/":
            self.handle_counter(read_counter)
        elif path == "/hit":
            self.handle_counter(increment_counter)
        else:
            self.send_json(404, {"error": "Unknown path"})

    def do_POST(self):
        if urlsplit(self.path).path in ("/", "/hit"):
            self.handle_counter(increment_counter)
        else:
            self.send_json(404, {"error": "Unknown path"})


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
