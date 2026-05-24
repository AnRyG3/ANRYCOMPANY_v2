from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request


ROOT = Path(r"F:\ANRYCAMPANY")
DEFAULT_OUT = ROOT / "reel_assets" / "generated_photos"
API_URL = "https://api.openai.com/v1/images/generations"
ENV_FILE = ROOT / ".env.local"


def ensure_inside_root(path: Path) -> Path:
    full = path.resolve()
    root = ROOT.resolve()
    try:
        full.relative_to(root)
    except ValueError as exc:
        raise SystemExit(f"Output path must be inside {root}") from exc
    return full


def post_json(url: str, api_key: str, payload: dict) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Image API error {exc.code}: {body}") from exc


def load_api_key() -> str | None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        return api_key.strip()
    if not ENV_FILE.exists():
        return None
    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == "OPENAI_API_KEY":
            return value.strip().strip('"').strip("'")
    return None


def safe_name(text: str) -> str:
    keep = []
    for ch in text:
        if ch.isalnum() or ch in ("-", "_"):
            keep.append(ch)
        elif ch in (" ", "　"):
            keep.append("_")
    name = "".join(keep).strip("_")
    return name[:80] or "generated_image"


def generate_one(prompt: str, out_path: Path, model: str, size: str, quality: str):
    api_key = load_api_key()
    if not api_key:
        raise SystemExit(
            "OPENAI_API_KEY is not set. Add it to F:\\ANRYCAMPANY\\.env.local as "
            "OPENAI_API_KEY=your_key, then run this F-drive tool again."
        )

    out_path = ensure_inside_root(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "quality": quality,
        "n": 1,
    }
    response = post_json(API_URL, api_key, payload)
    try:
        image_b64 = response["data"][0]["b64_json"]
    except (KeyError, IndexError, TypeError) as exc:
        raise SystemExit(f"Unexpected Image API response: {json.dumps(response, ensure_ascii=False)[:1000]}") from exc

    out_path.write_bytes(base64.b64decode(image_b64))
    return out_path


def read_prompt(args) -> str:
    if args.prompt:
        return args.prompt
    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise SystemExit("Provide --prompt, --prompt-file, or stdin.")


def main():
    parser = argparse.ArgumentParser(description="Generate an image and save it directly under F:\\ANRYCAMPANY.")
    parser.add_argument("--prompt", help="Prompt text.")
    parser.add_argument("--prompt-file", help="UTF-8 prompt text file.")
    parser.add_argument("--out", help="Output PNG path inside F:\\ANRYCAMPANY.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory inside F:\\ANRYCAMPANY.")
    parser.add_argument("--name", help="Output filename without extension.")
    parser.add_argument("--model", default="gpt-image-1", help="Image model.")
    parser.add_argument("--size", default="1024x1536", help="Image size, e.g. 1024x1536.")
    parser.add_argument("--quality", default="high", choices=["low", "medium", "high", "auto"])
    args = parser.parse_args()

    prompt = read_prompt(args).strip()
    if not prompt:
        raise SystemExit("Prompt is empty.")

    if args.out:
        out_path = Path(args.out)
    else:
        out_dir = ensure_inside_root(Path(args.out_dir))
        name = args.name or safe_name(prompt.splitlines()[0])
        out_path = out_dir / f"{name}.png"

    saved = generate_one(prompt, out_path, args.model, args.size, args.quality)
    print(saved)


if __name__ == "__main__":
    main()
