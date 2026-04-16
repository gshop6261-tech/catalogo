"""Download and optimize product images."""

import re
from pathlib import Path

import requests
from PIL import Image

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}

MAX_WIDTH = 1200
QUALITY = 85
TIMEOUT = 30


def _sanitize(url: str) -> str:
    return re.sub(r"[?#].*$", "", url.split("/")[-1])[:60]


def download_images(
    image_urls: list[str],
    product_id: int,
    root: Path,
) -> list[str]:
    """Download images and return list of relative paths from repo root."""
    dest_dir = root / "images" / "productos" / str(product_id)
    dest_dir.mkdir(parents=True, exist_ok=True)

    saved: list[str] = []
    for idx, url in enumerate(image_urls):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, stream=True)
            resp.raise_for_status()

            ext = ".jpg"
            ct = resp.headers.get("content-type", "")
            if "png" in ct:
                ext = ".png"
            elif "webp" in ct:
                ext = ".webp"

            filename = "main" + ext if idx == 0 else f"{idx + 1}{ext}"
            filepath = dest_dir / filename

            with open(filepath, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)

            final_path = _optimize(filepath)

            rel = final_path.relative_to(root).as_posix()
            saved.append(rel)
        except Exception as e:
            print(f"  Warning: failed to download {url}: {e}")
            continue

    return saved


def _optimize(path: Path) -> Path:
    try:
        img = Image.open(path)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        if img.width > MAX_WIDTH:
            ratio = MAX_WIDTH / img.width
            new_h = int(img.height * ratio)
            img = img.resize((MAX_WIDTH, new_h), Image.LANCZOS)

        out = path.with_suffix(".jpg")
        img.save(out, "JPEG", quality=QUALITY, optimize=True)
        if out != path:
            path.unlink(missing_ok=True)
        return out
    except Exception:
        return path
