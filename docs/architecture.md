# Architecture

## Components

### 1. Local WorkBuddy Skill

The local skill is the only supported write path. It:

- normalizes the original URL;
- calculates a deterministic Base62 ID;
- checks local data and remote KV for collisions;
- writes the minimal redirect record to KV;
- writes detailed private metadata to local Markdown and JSON;
- preserves the original ID when the destination later changes;
- verifies or repairs differences between local data and KV.

The local tool uses only the Python standard library.

### 2. Workers KV

KV is the online mapping store. Each key is a ShortRef ID. Each value is a minimal JSON object:

```json
{
  "version": 1,
  "url": "https://example.com/docs",
  "status": "active"
}
```

No title, project, tags, notes, source description, or history is uploaded.

### 3. Cloudflare Worker

The Worker accepts only `GET` and `HEAD`. It validates the ID, reads one KV key, validates the record, and returns a `302` redirect.

The Worker source contains no `put`, `delete`, or `list` call and exposes no write route. Cloudflare KV bindings are technically capable of writes, so this is a code-enforced read-only boundary rather than a separate Cloudflare read-only binding type.

## Data flow

```text
Create
URL -> normalize -> hash -> collision check -> KV PUT -> local index + Markdown

Resolve
GET /{id} -> validate ID -> KV GET -> validate target -> 302 Location

Migrate
local update -> KV PUT under same ID -> local history append
```

## Failure behavior

- Unknown, inactive, malformed, or invalid records return `404`.
- Unsupported HTTP methods return `405`.
- KV read failures return `503` with a short retry hint.
- Redirect responses are not browser-cached by ShortRef.
- KV is eventually consistent, so a new or changed mapping can take time to appear in every location.
