# Security model

## Public surface

The public service supports only:

```text
GET  /{8-12 character Base62 ID}
HEAD /{8-12 character Base62 ID}
```

There is no public write API or management UI. All other paths return `404`; all other methods return `405`.

## Cloudflare credentials

Use a dedicated Cloudflare API Token rather than a Global API Key.

Recommended scope:

- permission: **Workers KV Storage Write**;
- resource: the relevant Cloudflare account only;
- no zone-edit, DNS-edit, Worker-edit, or global account permissions unless separately required for deployment.

The token must be stored only in the environment variable named by `cloudflare.api_token_env`. The example uses `CLOUDFLARE_SHORTREF_TOKEN`.

## Privacy boundary

The destination URL is not secret. Anyone who knows or guesses the ShortRef ID can resolve it. Do not use ShortRef for URLs containing credentials, private access tokens, signed secrets, or sensitive query parameters.

The local tool rejects URLs with embedded username/password credentials, but it cannot reliably identify every secret query parameter.

## Read-only qualification

Cloudflare does not provide a separate read-only mode for a KV binding inside a Worker. The deployed code is read-only because it contains only `get()` and exposes no write path. Protecting the GitHub repository, Cloudflare account, and deployment permissions remains essential.

## Redirect policy

- Only `http` and `https` targets are accepted.
- Inactive or malformed records resolve as `404`.
- Redirects use `302`, not `301`.
- Responses use `Cache-Control: no-store` to preserve future migration control.
- The Worker does not log destination URLs in application code.
