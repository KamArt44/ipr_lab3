from http.server import HTTPServer, BaseHTTPRequestHandler 
from pathlib import Path
import json

DATA_FILE = Path("data/counter.txt")

def read_counter():
    if not DATA_FILE.exists():
        return 0
    return int(DATA_FILE.read_text(encoding ="utf-8"))

def write_counter(value):
    DATA_FILE.parent.mkdir(parents=True, exist_ok =True)
    DATA_FILE.write_text(str(value) + "\n", encoding= "utf-8")



class Handler(BaseHTTPRequestHandler ):
    def do_POST(self):
        try:
            counter = read_counter() +1
            write_counter(counter)
            self.do_GET()
        except OSError as error:
            response = json.dumps({"error": str(error)}).encode("utf-8")

            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(response)    



    def do_GET(self):
        counter = read_counter()
        response = json.dumps({"counter": counter}).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(response)
        



if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()