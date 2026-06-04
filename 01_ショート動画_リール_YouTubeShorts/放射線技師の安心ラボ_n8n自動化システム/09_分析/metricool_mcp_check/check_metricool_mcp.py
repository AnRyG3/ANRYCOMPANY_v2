import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT / ".env"
OUTPUT_DIR = ROOT / "output"
ENDPOINT = "https://ai.metricool.com/mcp"


def load_env():
    if not ENV_FILE.exists():
        return
    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def post(payload, session_id=None):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "X-Mc-Auth": API_KEY,
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            content_type = response.headers.get("Content-Type", "")
            body = response.read().decode("utf-8", errors="replace")
            result = parse_body(body, content_type)
            return result, response.headers.get("Mcp-Session-Id")
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Metricool MCP HTTP {error.code}: {body}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"Metricool MCP connection failed: {error.reason}") from error


def parse_body(body, content_type):
    if "text/event-stream" not in content_type:
        return json.loads(body) if body else {}
    events = []
    for line in body.splitlines():
        if line.startswith("data:"):
            events.append(json.loads(line[5:].strip()))
    return events[-1] if events else {}


load_env()
API_KEY = os.environ.get("METRICOOL_API_KEY", "").strip()
if not API_KEY or API_KEY == "ここにMetricoolのAPI Keyを入力":
    print("未設定: open_env.cmd を開き、Metricool API Keyを入力してください。")
    sys.exit(2)

initialize, session_id = post(
    {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "anrycampany-metricool-check", "version": "1.0.0"},
        },
    }
)
tools, _ = post({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}, session_id)

OUTPUT_DIR.mkdir(exist_ok=True)
output_path = OUTPUT_DIR / f"metricool_mcp_check_{datetime.now():%Y%m%d_%H%M%S}.json"
output_path.write_text(
    json.dumps({"initialize": initialize, "tools": tools}, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

tool_count = len(tools.get("result", {}).get("tools", []))
print("Metricool MCP 接続: 成功")
print(f"利用可能ツール数: {tool_count}")
print(f"確認結果: {output_path}")
