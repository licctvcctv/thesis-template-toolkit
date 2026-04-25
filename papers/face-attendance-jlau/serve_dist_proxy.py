from __future__ import annotations

import argparse
import http.client
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


def make_handler(root: Path, backend_host: str, backend_port: int):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self._handle()

        def do_POST(self):
            self._handle()

        def do_OPTIONS(self):
            self._handle()

        def _handle(self):
            parsed = urlsplit(self.path)
            if parsed.path.startswith("/springboot5s7063d3/"):
                self._proxy()
            else:
                self._static(parsed.path)

        def _proxy(self):
            body = self.rfile.read(int(self.headers.get("Content-Length", "0") or 0))
            conn = http.client.HTTPConnection(backend_host, backend_port, timeout=30)
            headers = {k: v for k, v in self.headers.items() if k.lower() not in {"host", "content-length"}}
            conn.request(self.command, self.path, body=body, headers=headers)
            resp = conn.getresponse()
            data = resp.read()
            self.send_response(resp.status)
            for k, v in resp.getheaders():
                if k.lower() not in {"transfer-encoding", "connection", "content-encoding"}:
                    self.send_header(k, v)
            self.end_headers()
            self.wfile.write(data)
            conn.close()

        def _static(self, path: str):
            rel = path.lstrip("/") or "index.html"
            target = (root / rel).resolve()
            if not str(target).startswith(str(root.resolve())) or not target.exists() or target.is_dir():
                target = root / "index.html"
            data = target.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", mimetypes.guess_type(target.name)[0] or "application/octet-stream")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, fmt, *args):
            return

    return Handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--backend-host", default="127.0.0.1")
    parser.add_argument("--backend-port", type=int, default=8080)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    httpd = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(root, args.backend_host, args.backend_port))
    print(f"serving {root} on http://127.0.0.1:{args.port}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
