# ShortRef

ShortRef is a small personal reference service for stable links such as:

```text
https://reference.gany.app/qeoLCypr
```

It deliberately separates private link management from the public redirect path:

```text
Local WorkBuddy Skill  --write-->  Cloudflare Workers KV  --read-->  Cloudflare Worker
       private records                 minimal mapping                 302 redirect
```

The public Worker has no creation endpoint, management page, login system, cookie, session, or API token. Detailed titles, project names, tags, notes, and migration history remain in local Markdown and JSON files.

## Repository layout

```text
ShortRef/
├── worker/                 Cloudflare Worker; GET/HEAD and KV reads only
├── skill/shortref/         WorkBuddy Skill and standard-library Python CLI
├── docs/                   Architecture, protocol, deployment, and security
└── .github/workflows/      Dependency-free test workflow
```

## Design principles

- `reference.gany.app/{id}` is the stable public identifier.
- IDs are deterministic: normalized URL → SHA-256 → Base62 → 8 characters.
- Hash collisions extend the ID one character at a time, up to 12 characters.
- The ID remains fixed after creation; the destination can be migrated later.
- Redirects use `302` and `Cache-Control: no-store` so destination changes remain possible.
- Cloudflare KV stores only `{ version, url, status }`.
- Local data is authoritative for descriptive metadata and change history.

## Quick start

1. Deploy the Worker and create or attach its KV namespace. See [`docs/deployment.md`](docs/deployment.md).
2. Bind the Worker to `reference.gany.app`.
3. Install `skill/shortref` in WorkBuddy.
4. Copy `skill/shortref/templates/config.example.json` to a private local path.
5. Set `SHORTREF_CONFIG` and `CLOUDFLARE_SHORTREF_TOKEN` locally.
6. Create a reference:

```bash
python skill/shortref/scripts/shortref.py create "https://example.com/docs" \
  --title "Example documentation" \
  --project "Example"
```

## Validation

```bash
cd worker
npm run check

cd ..
python -m unittest discover -s skill/shortref/tests -v
```

## Status

The current version is intentionally narrow. It is a personal stable-reference layer, not a public URL-shortening platform.

## License

MIT
