"""XUnity CustomTranslate 回显服务：原样返回文本，并把每条请求记到 logs/captured_texts.jsonl。

用法：python capture_server.py  （监听 127.0.0.1:18080，Ctrl+C 结束）
"""
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from common import LOGS_DIR

LOG = LOGS_DIR / "captured_texts.jsonl"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        q = parse_qs(urlparse(self.path).query, keep_blank_values=True)
        text = q.get("text", [""])[0]
        with LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"t": time.strftime("%H:%M:%S"), "text": text}, ensure_ascii=False) + "\n")
        body = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 18080), Handler).serve_forever()
