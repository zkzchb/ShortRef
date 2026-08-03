# Data model

## Remote KV record

Only redirect-critical data is stored online:

```json
{
  "version": 1,
  "url": "https://example.com/docs-v2",
  "status": "active"
}
```

- `version`: remote schema version.
- `url`: current redirect target.
- `status`: `active` or `inactive`.

## Local index

`index.json` is the local machine-readable record. It contains each ID, original source URL, current target, local metadata, timestamps, and history.

The original `source_url` remains unchanged after migration. `target_url` is the current destination.

## Local Markdown

Each reference also has `records/{id}.md`. Markdown is generated from the local index and is intended for human reading. It can contain private contextual information such as title, project, tags, notes, purpose, usage locations, and destination migration history.

The local data directory is deliberately outside this repository and should not be synchronized publicly.

## Backups

Before each local mutation, ShortRef copies the existing index into `backups/`. The number of retained backups is controlled by `storage.backup_limit`.
