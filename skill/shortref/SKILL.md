---
name: shortref
description: Create and maintain private local ShortRef records while publishing only minimal redirect mappings to Cloudflare Workers KV.
---

# ShortRef

Use this skill when the user asks to create, inspect, migrate, disable, enable, verify, or synchronize a ShortRef link under `reference.gany.app`.

## Safety boundary

- The Cloudflare Worker is read-only by code and has no public write endpoint.
- Write to KV only through `scripts/shortref.py` on the local machine.
- Never put a Cloudflare token in this skill, Git, Markdown, or `config.json`.
- Read the token from the environment variable named by `cloudflare.api_token_env`.
- Keep detailed title, project, tags, notes, and history only in the configured local data directory.
- Do not shorten secret, credential-bearing, or access-token URLs. The redirect destination is not private.

## Configuration

Resolve configuration in this order:

1. `--config PATH`
2. `SHORTREF_CONFIG`
3. `~/.shortref/config.json`

Before first use, copy `templates/config.example.json` outside the skill directory and fill in the Cloudflare account ID, KV namespace ID, base URL, and local data directory.

## Operations

Create a deterministic reference:

```bash
python scripts/shortref.py create "<URL>" --title "<TITLE>" --project "<PROJECT>" --tag "<TAG>" --notes "<NOTES>"
```

Change the destination without changing the reference ID:

```bash
python scripts/shortref.py update <ID> "<NEW_URL>" --reason "<REASON>"
```

Disable or enable:

```bash
python scripts/shortref.py disable <ID> --reason "<REASON>"
python scripts/shortref.py enable <ID> --reason "<REASON>"
```

Inspect and list:

```bash
python scripts/shortref.py show <ID>
python scripts/shortref.py list
```

Verify or repair synchronization:

```bash
python scripts/shortref.py verify [ID]
python scripts/shortref.py sync [ID]
python scripts/shortref.py sync [ID] --apply
```

Always run `sync` once without `--apply` before allowing it to modify KV. Report the resulting short URL and whether the operation created, reused, updated, or synchronized a record.
