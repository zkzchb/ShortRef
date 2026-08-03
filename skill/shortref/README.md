# ShortRef WorkBuddy Skill

This directory is safe to install or copy as a WorkBuddy skill. It contains no personal configuration, API token, or private link record.

## Local setup

1. Copy `templates/config.example.json` to a private location.
2. Set its `data_dir`, Cloudflare account ID, and KV namespace ID.
3. Create a Cloudflare API Token limited to the relevant account with **Workers KV Storage Write** permission.
4. Store the token in the environment variable `CLOUDFLARE_SHORTREF_TOKEN`.
5. Set `SHORTREF_CONFIG` to the private config file path.

PowerShell example:

```powershell
$env:SHORTREF_CONFIG = "D:\ShortRef\config.json"
$env:CLOUDFLARE_SHORTREF_TOKEN = "your-token"
python .\scripts\shortref.py create "https://example.com/docs" --title "Example docs"
```

## Local data

The script creates:

```text
ShortRefData/
├── index.json
├── records/
│   └── Ab12Cd34.md
└── backups/
    └── index-*.json
```

`index.json` is the machine-readable source for the local tool. Markdown files are human-readable private records. KV receives only `version`, `url`, and `status`.
