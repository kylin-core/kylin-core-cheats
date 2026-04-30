#!/usr/bin/env python3
"""Fetch PlayStation title metadata and media from Sony TMDB."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import html
import json
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
TITLES_DIR = ROOT / "titles"
HMAC_SHA1_KEY = bytes.fromhex(
    "F5DE66D2680E255B2DF79E74F890EBF349262F618BCAE2A9ACCDEE5156CE8DF2CDF2D48C71173CDC2594465B87405D197CF1AED3B7E9671EEB56CA6753C2E6B0"
)
MEDIA_TIMEOUT_SECONDS = 20
LANGUAGE_PRIORITY = ("zh-CN", "zh-Hans", "zh-TW", "en", "en-US", "en-GB")
STORE_HASH_PRODUCT_BY_ID = "a128042177bd93dd831164103d53b73ef790d56f51dae647064cb8f9d9fc9d1a"
STORE_LOCALES = ("en-US", "en-GB", "zh-Hans", "zh-Hant", "ja-JP")
MEDIA_ROLE_PRIORITY = {
    "iconImage": ("MASTER", "GAMEHUB_COVER_ART", "PORTRAIT_BANNER", "FOUR_BY_THREE_BANNER"),
    "coverImage": ("GAMEHUB_COVER_ART", "PORTRAIT_BANNER", "MASTER", "FOUR_BY_THREE_BANNER"),
    "backgroundImage": ("BACKGROUND", "BACKGROUND_LAYER_ART", "FOUR_BY_THREE_BANNER", "MASTER"),
}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def tmdb_url(title_id: str) -> tuple[str, str]:
    np_title_id = f"{title_id}_00"
    digest = hmac.new(HMAC_SHA1_KEY, np_title_id.encode("utf-8"), hashlib.sha1).hexdigest().upper()
    return np_title_id, (
        f"https://tmdb.np.dl.playstation.net/tmdb2/"
        f"{np_title_id}_{digest}/{np_title_id}.json"
    )


def fetch_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "KylinCoreCheats/1.0"})
    with urlopen(request, timeout=MEDIA_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=MEDIA_TIMEOUT_SECONDS) as response:
        return response.read().decode("utf-8", "replace")


def fetch_prospero(title_id: str) -> dict:
    page = fetch_text(f"https://prosperopatches.com/{title_id}")
    metadata: dict[str, str] = {}
    patterns = {
        "name": rf"<h1[^>]*>\s*([^<]+)\s*</h1>\s*<p[^>]*>\s*{re.escape(title_id)}\s*</p>",
        "contentId": r"Content ID\s*</[^>]+>\s*<[^>]+>\s*([^<]+)",
        "publisher": r"Publisher\s*</[^>]+>\s*<[^>]+>\s*(?:<[^>]+>)*\s*([^<]+)",
        "region": r"Region\s*</[^>]+>\s*<[^>]+>\s*([^<]+)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, page, re.IGNORECASE | re.DOTALL)
        if match:
            metadata[key] = html.unescape(re.sub(r"\s+", " ", match.group(1))).strip()
    return metadata


def store_locale_candidates(region: str | None) -> tuple[str, ...]:
    if region == "EU":
        return ("en-GB", "en-US", "zh-Hans", "zh-Hant", "ja-JP")
    if region in {"US", "NA"}:
        return ("en-US", "en-GB", "zh-Hans", "zh-Hant", "ja-JP")
    if region == "JP":
        return ("ja-JP", "en-US", "en-GB", "zh-Hans", "zh-Hant")
    return STORE_LOCALES


def fetch_store_product(product_id: str, locales: tuple[str, ...]) -> tuple[dict, str]:
    variables = json.dumps({"productId": product_id}, separators=(",", ":"))
    extensions = json.dumps(
        {"persistedQuery": {"version": 1, "sha256Hash": STORE_HASH_PRODUCT_BY_ID}},
        separators=(",", ":"),
    )
    query = urlencode(
        {
            "operationName": "metGetProductById",
            "variables": variables,
            "extensions": extensions,
        }
    )
    last_error = "not requested"
    for locale in locales:
        url = f"https://web.np.playstation.com/api/graphql/v1/op?{query}"
        request = Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "content-type": "application/json",
                "x-psn-store-locale-override": locale,
            },
        )
        try:
            with urlopen(request, timeout=MEDIA_TIMEOUT_SECONDS) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            last_error = f"{locale} HTTP {exc.code}"
            continue
        product = payload.get("data", {}).get("productRetrieve")
        if product:
            return product, locale
        errors = payload.get("errors") or []
        last_error = errors[0].get("message", f"{locale} product not found") if errors else last_error
    raise LookupError(last_error)


def choose_localized(items: list[dict], value_key: str) -> str | None:
    if not items:
        return None
    by_lang = {item.get("lang"): item for item in items if item.get("lang")}
    for lang in LANGUAGE_PRIORITY:
        value = by_lang.get(lang, {}).get(value_key)
        if value:
            return value
    return items[0].get(value_key)


def file_suffix(url: str, fallback: str) -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp"}:
        return suffix
    return fallback


def download(url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": "KylinCoreCheats/1.0"})
    with urlopen(request, timeout=MEDIA_TIMEOUT_SECONDS) as response:
        with tempfile.NamedTemporaryFile(delete=False, dir=str(output_path.parent)) as handle:
            shutil.copyfileobj(response, handle)
            temp_path = Path(handle.name)
    temp_path.replace(output_path)


def normalize_image_extension(path: Path) -> Path:
    with path.open("rb") as handle:
        header = handle.read(12)
    if header.startswith(b"\xff\xd8\xff"):
        expected = ".jpg"
    elif header.startswith(b"\x89PNG\r\n\x1a\n"):
        expected = ".png"
    elif header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        expected = ".webp"
    else:
        return path

    if path.suffix.lower() == expected:
        return path
    normalized = path.with_suffix(expected)
    path.replace(normalized)
    return normalized


def media_url_by_role(media: list[dict], roles: tuple[str, ...]) -> str | None:
    role_map = {
        item.get("role"): item.get("url")
        for item in media or []
        if item.get("type") == "IMAGE" and item.get("url")
    }
    for role in roles:
        if role_map.get(role):
            return role_map[role]
    return None


def download_media_set(title: dict, title_path: Path, urls: dict[str, str], download_assets: bool) -> None:
    media_dir = title_path.parent / "media"
    file_stems = {
        "iconImage": "icon",
        "coverImage": "cover",
        "backgroundImage": "background",
    }
    for key, url in urls.items():
        if not url:
            continue
        if not download_assets:
            title[key] = url
            continue
        output_path = media_dir / f"{file_stems[key]}{file_suffix(url, '.jpg')}"
        try:
            download(url, output_path)
            output_path = normalize_image_extension(output_path)
            title[key] = output_path.relative_to(ROOT).as_posix()
        except (HTTPError, URLError, TimeoutError) as exc:
            print(f"warning: {title['titleId']}: {key} download failed: {exc}")


def enrich_from_tmdb(title: dict, title_path: Path, download_assets: bool) -> tuple[bool, str]:
    title = load_json(title_path)
    title_id = title["titleId"]
    np_title_id, url = tmdb_url(title_id)

    try:
        info = fetch_json(url)
    except HTTPError as exc:
        return False, f"TMDB HTTP {exc.code}"
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        return False, f"TMDB fetch failed: {exc}"

    name = choose_localized(info.get("names", []), "name")
    icon_url = choose_localized(info.get("icons", []), "icon")
    background_url = info.get("backgroundImage")

    title["name"] = name or title.get("name") or title_id
    title["platforms"] = [info.get("console", "PS5")]
    title["contentId"] = info.get("contentId", title.get("contentId", ""))
    title["metadataSource"] = "sony-tmdb"
    title["metadataUpdatedAt"] = now_utc()
    title["notes"] = title.get("notes", "Generated from published cheat metadata.")

    urls = {"iconImage": icon_url, "backgroundImage": background_url}
    if background_url:
        urls["coverImage"] = background_url
    download_media_set(title, title_path, urls, download_assets)

    title["npTitleId"] = np_title_id
    write_json(title_path, {k: v for k, v in title.items() if v not in ("", [], None)})
    return True, "enriched from Sony TMDB"


def enrich_from_store(title: dict, title_path: Path, download_assets: bool) -> tuple[bool, str]:
    title_id = title["titleId"]
    prospero: dict[str, str] = {}
    product_id = title.get("contentId")
    if not product_id:
        prospero = fetch_prospero(title_id)
        product_id = prospero.get("contentId")
    if not product_id:
        return False, "PROSPEROPatches content ID not found"

    product, locale = fetch_store_product(product_id, store_locale_candidates(prospero.get("region")))
    concept = product.get("concept") or {}
    media = product.get("media") or concept.get("media") or []
    urls = {
        key: media_url_by_role(media, roles)
        for key, roles in MEDIA_ROLE_PRIORITY.items()
    }

    title["name"] = product.get("name") or concept.get("name") or prospero.get("name") or title.get("name") or title_id
    title["platforms"] = product.get("platforms") or title.get("platforms") or ["PS5"]
    title["publisher"] = product.get("publisherName") or concept.get("publisherName") or prospero.get("publisher")
    title["contentId"] = product_id
    title["npTitleId"] = product.get("npTitleId") or f"{title_id}_00"
    title["releaseDate"] = product.get("releaseDate") or concept.get("releaseDate", {}).get("value")
    title["storeUrl"] = f"https://store.playstation.com/{locale.lower()}/product/{product_id}"
    title["metadataSource"] = "prosperopatches+playstation-store"
    title["metadataUpdatedAt"] = now_utc()
    title["notes"] = title.get("notes", "Generated from published cheat metadata.")
    download_media_set(title, title_path, {k: v for k, v in urls.items() if v}, download_assets)
    write_json(title_path, {k: v for k, v in title.items() if v not in ("", [], None)})
    return True, f"enriched from PlayStation Store via {locale}"


def enrich_title(title_path: Path, download_assets: bool) -> tuple[bool, str]:
    title = load_json(title_path)
    title_id = title["titleId"]

    try:
        tmdb_ok, tmdb_message = enrich_from_tmdb(title, title_path, download_assets)
    except ValueError as exc:
        tmdb_ok, tmdb_message = False, f"TMDB media failed: {exc}"
    if tmdb_ok:
        return True, f"{title_id}: {tmdb_message}"

    try:
        store_ok, store_message = enrich_from_store(title, title_path, download_assets)
    except HTTPError as exc:
        return False, f"{title_id}: {tmdb_message}; Store HTTP {exc.code}"
    except (URLError, TimeoutError, LookupError, ValueError, json.JSONDecodeError) as exc:
        return False, f"{title_id}: {tmdb_message}; Store fetch failed: {exc}"
    if store_ok:
        return True, f"{title_id}: {store_message}"
    return False, f"{title_id}: {tmdb_message}; {store_message}"


def iter_title_paths(title_ids: list[str]) -> list[Path]:
    if title_ids:
        return [TITLES_DIR / title_id / "title.json" for title_id in title_ids]
    return sorted(TITLES_DIR.glob("*/title.json"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("title_ids", nargs="*", help="Optional title IDs, for example PPSA04609.")
    parser.add_argument(
        "--no-download-assets",
        action="store_true",
        help="Store remote media URLs instead of downloading files under titles/<TITLE_ID>/media/.",
    )
    args = parser.parse_args()

    ok = 0
    failed = 0
    for title_path in iter_title_paths(args.title_ids):
        if not title_path.exists():
            print(f"warning: {title_path.relative_to(ROOT)} does not exist")
            failed += 1
            continue
        changed, message = enrich_title(title_path, download_assets=not args.no_download_assets)
        print(message)
        if changed:
            ok += 1
        else:
            failed += 1

    print(f"done: {ok} enriched, {failed} skipped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
