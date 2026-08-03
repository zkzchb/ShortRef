# Deployment

## 1. Deploy the Worker

From the Worker directory:

```bash
cd worker
npm install
npx wrangler login
npm run deploy:dry
npm run deploy
```

`wrangler.jsonc` defines the `SHORTREF_KV` binding without a namespace ID. On a first Wrangler deployment, Cloudflare can provision the namespace and update the local configuration. If you prefer, create a KV namespace manually and add its ID to the binding:

```jsonc
"kv_namespaces": [
  {
    "binding": "SHORTREF_KV",
    "id": "YOUR_NAMESPACE_ID"
  }
]
```

## 2. Attach the custom domain

In Cloudflare Workers & Pages:

1. Open the `shortref` Worker.
2. Open **Settings → Domains & Routes**.
3. Add the Custom Domain `reference.gany.app`.
4. Confirm the domain is active.

## 3. Create the local token

Create a dedicated API Token in Cloudflare with **Workers KV Storage Write** permission for the relevant account. Record the account ID and the ShortRef KV namespace ID. Do not use the Global API Key.

## 4. Configure the local skill

Copy `skill/shortref/templates/config.example.json` into a private local directory, then set the local data directory, account ID, namespace ID, and token environment-variable name.

PowerShell example:

```powershell
$env:SHORTREF_CONFIG = "D:\ShortRef\config.json"
$env:CLOUDFLARE_SHORTREF_TOKEN = "your-token"
```

## 5. Test end to end

```powershell
python .\skill\shortref\scripts\shortref.py create `
  "https://example.com/docs" `
  --title "Example documentation"
```

Open the returned `https://reference.gany.app/{id}` URL. A new or changed KV value can take time to become visible in every Cloudflare location because KV is eventually consistent.

## Updating code

```bash
cd worker
npm run check
npm run deploy:dry
```

No Cloudflare API token is needed by the Worker at runtime. The KV binding is its only runtime dependency.
