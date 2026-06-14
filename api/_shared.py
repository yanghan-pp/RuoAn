from http.server import BaseHTTPRequestHandler
from pathlib import Path
import importlib.util
import json


ROOT = Path(__file__).resolve().parents[1]
CORE_CANDIDATES = [
    Path(__file__).resolve().parent / "lianlian_core.py",
    ROOT / "outputs" / "agent-network-server.py",
]
_core = None


def load_core():
    core_path = next((path for path in CORE_CANDIDATES if path.exists()), None)
    if core_path is None:
        candidates = ", ".join(str(path) for path in CORE_CANDIDATES)
        raise FileNotFoundError(f"Backend core file is missing. Checked: {candidates}")
    spec = importlib.util.spec_from_file_location("lianlian_core", core_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load backend core from: {core_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_core():
    global _core
    if _core is None:
        _core = load_core()
    return _core


class JsonHandler(BaseHTTPRequestHandler):
    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        return json.loads(raw or "{}")

    def send_json(self, payload, code=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, exc):
        self.send_json({"error": "server_error", "detail": str(exc)}, 500)
