# Architecture

[English](architecture.md) | [简体中文](architecture-zhcn.md)

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

The Worker accepts only `GET` and `HEAD`:

- `/` returns the generic service page with status `200`;
- a valid active ID reads one KV key and returns a `302` redirect;
- an invalid, unknown, inactive, or malformed reference returns the generic page with status `404`.

The two HTML pages live in `worker/public/` and are deployed as a static-assets binding named `ASSETS`. `run_worker_first: true` ensures the Worker keeps control of routing and explicitly selects each page through `env.ASSETS`.

The Worker source contains no `put`, `delete`, or `list` call and exposes no write route. Cloudflare KV bindings are technically capable of writes, so this is a code-enforced read-only boundary rather than a separate Cloudflare read-only binding type.

## Data flow

```text
Create
URL -> normalize -> hash -> collision check -> KV PUT -> local index + Markdown

Resolve
GET /{id} -> validate ID -> KV GET -> validate target -> 302 Location

Render page
GET / -> Worker -> ASSETS/index.html -> 200
invalid reference -> Worker -> ASSETS/404.html -> 404

Migrate
local update -> KV PUT under same ID -> local history append
```

## Failure behavior

- Unknown, inactive, malformed, or invalid records return the generic HTML page with status `404`.
- Unsupported HTTP methods return `405`.
- KV or page-asset failures return `503` with a short retry hint.
- Redirect and HTML responses use `Cache-Control: no-store`.
- KV is eventually consistent, so a new or changed mapping can take time to appear in every location.
