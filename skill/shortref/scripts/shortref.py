#!/usr/bin/env python3
"""Local ShortRef manager. Detailed records stay local; KV receives only redirect data."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
ID_RE = re.compile(r"^[0-9A-Za-z]{8,12}$")
HASH_PROTOCOL = "sha256-base62-v1"


class ShortRefError(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def normalize_url(value: str) -> str:
    value = value.strip()
    try:
        parts = urllib.parse.urlsplit(value)
    except ValueError as exc:
        raise ShortRefError(f"Invalid URL: {exc}") from exc
    scheme = parts.scheme.lower()
    if scheme not in {"http", "https"} or not parts.hostname:
        raise ShortRefError("Only absolute http/https URLs are supported")
    if parts.username is not None or parts.password is not None:
        raise ShortRefError("Embedded URL credentials are not allowed")
    try:
        port = parts.port
    except ValueError as exc:
        raise ShortRefError(f"Invalid port: {exc}") from exc
    host = parts.hostname.encode("idna").decode("ascii").lower()
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    default = (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
    netloc = host if port is None or default else f"{host}:{port}"
    return urllib.parse.urlunsplit((scheme, netloc, parts.path or "/", parts.query, parts.fragment))


def base62(number: int) -> str:
    if number == 0:
        return "0"
    chars: list[str] = []
    while number:
        number, remainder = divmod(number, 62)
        chars.append(ALPHABET[remainder])
    return "".join(reversed(chars))


def hash_token(url: str) -> str:
    digest = hashlib.sha256(url.encode("utf-8")).digest()
    return base62(int.from_bytes(digest, "big")).rjust(43, "0")


def load_config(path_arg: str | None) -> tuple[dict[str, Any], Path]:
    raw = path_arg or os.getenv("SHORTREF_CONFIG") or "~/.shortref/config.json"
    path = Path(os.path.expandvars(os.path.expanduser(raw))).resolve()
    if not path.is_file():
        raise ShortRefError(f"Config not found: {path}")
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ShortRefError(f"Cannot read config: {exc}") from exc
    data_dir = Path(os.path.expandvars(os.path.expanduser(config["data_dir"])))
    if not data_dir.is_absolute():
        data_dir = (path.parent / data_dir).resolve()
    config["data_dir"] = str(data_dir)
    config["base_url"] = config["base_url"].rstrip("/")
    return config, path


def paths(config: dict[str, Any]) -> tuple[Path, Path, Path]:
    root = Path(config["data_dir"])
    records = root / "records"
    backups = root / "backups"
    records.mkdir(parents=True, exist_ok=True)
    backups.mkdir(parents=True, exist_ok=True)
    index = root / "index.json"
    if not index.exists():
        atomic_json(index, {"version": 1, "links": {}})
    return index, records, backups


def atomic_json(path: Path, value: Any) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def load_index(config: dict[str, Any]) -> tuple[dict[str, Any], Path, Path, Path]:
    index_path, records, backups = paths(config)
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ShortRefError(f"Cannot read local index: {exc}") from exc
    if index.get("version") != 1 or not isinstance(index.get("links"), dict):
        raise ShortRefError("Unsupported or malformed local index")
    return index, index_path, records, backups


def remote_payload(record: dict[str, Any]) -> dict[str, Any]:
    return {"version": 1, "url": record["target_url"], "status": record["status"]}


class KV:
    def __init__(self, config: dict[str, Any]) -> None:
        cf = config["cloudflare"]
        token_name = cf.get("api_token_env", "CLOUDFLARE_SHORTREF_TOKEN")
        token = os.getenv(token_name)
        if not token:
            raise ShortRefError(f"Environment variable {token_name} is not set")
        self.token = token
        self.endpoint = (
            "https://api.cloudflare.com/client/v4/accounts/"
            f"{cf['account_id']}/storage/kv/namespaces/{cf['namespace_id']}/values"
        )

    def request(self, key: str, method: str, value: dict[str, Any] | None = None) -> Any:
        url = f"{self.endpoint}/{urllib.parse.quote(key, safe='')}"
        data = None if value is None else json.dumps(value, separators=(",", ":")).encode()
        headers = {"Authorization": f"Bearer {self.token}", "User-Agent": "ShortRef/0.1"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            if method == "GET" and exc.code == 404:
                return None
            detail = exc.read().decode("utf-8", errors="replace")
            raise ShortRefError(f"Cloudflare KV {method} failed ({exc.code}): {detail}") from exc
        except urllib.error.URLError as exc:
            raise ShortRefError(f"Cloudflare KV request failed: {exc.reason}") from exc
        if method == "GET":
            try:
                return json.loads(body)
            except json.JSONDecodeError as exc:
                raise ShortRefError(f"KV key {key} is not valid JSON") from exc
        if body:
            try:
                envelope = json.loads(body)
                if envelope.get("success") is False:
                    raise ShortRefError(f"Cloudflare rejected write: {envelope.get('errors')}")
            except json.JSONDecodeError:
                pass
        return None

    def get(self, key: str) -> Any:
        return self.request(key, "GET")

    def put(self, key: str, value: dict[str, Any]) -> None:
        self.request(key, "PUT", value)


def markdown(record: dict[str, Any]) -> str:
    front = {
        "id": record["id"], "short_url": record["short_url"],
        "source_url": record["source_url"], "target_url": record["target_url"],
        "status": record["status"], "title": record.get("title", ""),
        "project": record.get("project", ""), "tags": record.get("tags", []),
        "created_at": record["created_at"], "updated_at": record["updated_at"],
        "hash_algorithm": HASH_PROTOCOL,
    }
    lines = ["---"] + [f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in front.items()]
    lines += ["---", "", f"# {record.get('title') or record['id']}", "", "## Notes", "", record.get("notes") or "", "", "## History", ""]
    for item in record.get("history", []):
        lines.append(f"- {item['at']}: {item['action']}" + (f" — {item.get('reason')}" if item.get("reason") else ""))
    return "\n".join(lines).rstrip() + "\n"


def save(config: dict[str, Any], index: dict[str, Any], record: dict[str, Any]) -> None:
    index_path, records, backups = paths(config)
    if index_path.exists():
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        shutil.copy2(index_path, backups / f"index-{stamp}.json")
    limit = int(config.get("storage", {}).get("backup_limit", 30))
    for old in sorted(backups.glob("index-*.json"))[:-limit]:
        old.unlink(missing_ok=True)
    atomic_json(index_path, index)
    (records / f"{record['id']}.md").write_text(markdown(record), encoding="utf-8")


def checked_id(value: str) -> str:
    if not ID_RE.fullmatch(value):
        raise ShortRefError("ID must be 8-12 Base62 characters")
    return value


def create(args: argparse.Namespace, config: dict[str, Any], kv: KV) -> None:
    index, _, _, _ = load_index(config)
    source = normalize_url(args.url)
    for record in index["links"].values():
        if record["source_url"] == source:
            print(record["short_url"]); return
    lengths = config.get("hash", {})
    token = hash_token(source)
    selected = None
    for size in range(int(lengths.get("initial_length", 8)), int(lengths.get("max_length", 12)) + 1):
        candidate = token[:size]
        local = index["links"].get(candidate)
        if local and local["source_url"] != source:
            continue
        remote = kv.get(candidate)
        if remote is None or remote == {"version": 1, "url": source, "status": "active"}:
            selected = candidate; break
    if selected is None:
        raise ShortRefError("Hash collision range exhausted")
    timestamp = now()
    record = {
        "id": selected, "short_url": f"{config['base_url']}/{selected}",
        "source_url": source, "target_url": source, "status": "active",
        "title": args.title or "", "project": args.project or "",
        "tags": sorted(set(args.tag or [])), "notes": args.notes or "",
        "created_at": timestamp, "updated_at": timestamp,
        "history": [{"at": timestamp, "action": "created"}],
    }
    kv.put(selected, remote_payload(record))
    index["links"][selected] = record
    save(config, index, record)
    print(record["short_url"])


def mutate(args: argparse.Namespace, config: dict[str, Any], kv: KV, action: str) -> None:
    index, _, _, _ = load_index(config)
    ref_id = checked_id(args.id)
    record = index["links"].get(ref_id)
    if not record:
        raise ShortRefError(f"Local reference not found: {ref_id}")
    updated = dict(record); timestamp = now()
    if action == "update":
        old = record["target_url"]
        updated["target_url"] = normalize_url(args.url)
        history = {"at": timestamp, "action": "target_updated", "from": old, "to": updated["target_url"]}
    else:
        updated["status"] = "inactive" if action == "disable" else "active"
        history = {"at": timestamp, "action": f"status_{updated['status']}"}
    if getattr(args, "reason", None): history["reason"] = args.reason
    updated["updated_at"] = timestamp
    updated["history"] = list(record.get("history", [])) + [history]
    kv.put(ref_id, remote_payload(updated))
    index["links"][ref_id] = updated
    save(config, index, updated)
    print(updated["short_url"])


def show_or_list(args: argparse.Namespace, config: dict[str, Any]) -> None:
    index, _, _, _ = load_index(config)
    if args.command == "show":
        record = index["links"].get(checked_id(args.id))
        if not record: raise ShortRefError("Local reference not found")
        print(json.dumps(record, ensure_ascii=False, indent=2)); return
    for record in sorted(index["links"].values(), key=lambda x: x["created_at"]):
        if not args.status or record["status"] == args.status:
            print(f"{record['id']}\t{record['status']}\t{record.get('title') or '-'}\t{record['target_url']}")


def verify(args: argparse.Namespace, config: dict[str, Any], kv: KV, apply: bool) -> None:
    index, _, _, _ = load_index(config)
    records = [index["links"].get(checked_id(args.id))] if args.id else list(index["links"].values())
    if any(record is None for record in records): raise ShortRefError("Local reference not found")
    mismatches = []
    for record in records:
        expected = remote_payload(record); actual = kv.get(record["id"])
        if actual == expected: print(f"OK       {record['id']}")
        else: mismatches.append(record); print(f"MISMATCH {record['id']}")
    if apply:
        for record in mismatches: kv.put(record["id"], remote_payload(record)); print(f"SYNCED   {record['id']}")
    elif mismatches and args.command == "sync":
        print("Dry run only; add --apply to write KV")
    elif mismatches:
        raise ShortRefError(f"Verification found {len(mismatches)} mismatch(es)")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Manage ShortRef locally and write minimal mappings to Cloudflare KV")
    p.add_argument("--config")
    sub = p.add_subparsers(dest="command", required=True)
    c = sub.add_parser("create"); c.add_argument("url"); c.add_argument("--title"); c.add_argument("--project"); c.add_argument("--tag", action="append", default=[]); c.add_argument("--notes")
    u = sub.add_parser("update"); u.add_argument("id"); u.add_argument("url"); u.add_argument("--reason")
    for name in ("disable", "enable"):
        q = sub.add_parser(name); q.add_argument("id"); q.add_argument("--reason")
    s = sub.add_parser("show"); s.add_argument("id")
    l = sub.add_parser("list"); l.add_argument("--status", choices=["active", "inactive"])
    v = sub.add_parser("verify"); v.add_argument("id", nargs="?")
    y = sub.add_parser("sync"); y.add_argument("id", nargs="?"); y.add_argument("--apply", action="store_true")
    return p


def main() -> int:
    args = parser().parse_args()
    try:
        config, _ = load_config(args.config)
        if args.command in {"show", "list"}: show_or_list(args, config); return 0
        kv = KV(config)
        if args.command == "create": create(args, config, kv)
        elif args.command in {"update", "disable", "enable"}: mutate(args, config, kv, args.command)
        else: verify(args, config, kv, bool(getattr(args, "apply", False)))
        return 0
    except (ShortRefError, KeyError, TypeError, ValueError) as exc:
        print(f"ShortRef error: {exc}", file=sys.stderr); return 1


if __name__ == "__main__":
    raise SystemExit(main())
