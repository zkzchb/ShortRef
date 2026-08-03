# ShortRef Worker

[English](README.md) | [简体中文](README-zhcn.md)

The public half of ShortRef exposes three responses:

```text
GET /       -> 200 service page
GET /{id}  -> read SHORTREF_KV -> 302 redirect
other path -> 404 reference page
```

There is no public creation endpoint, dashboard, authentication system, cookie, session, or write path. The service and 404 pages are generic and contain no deployment-specific domain.

## Static pages

```text
public/
├── index.html
└── 404.html
```

`wrangler.jsonc` configures this directory as a static-assets binding named `ASSETS` with `run_worker_first: true`. The Worker therefore handles every request first and loads either page through `env.ASSETS`. Worker code and pages are published together by the same deployment command.

## Commands

```bash
npm install
npm test
npm run dev
npm run deploy:dry
npm run deploy
```

The first deployment can automatically provision the KV namespace because the binding in `wrangler.jsonc` omits an ID. After deployment, copy the namespace ID from Cloudflare into the local WorkBuddy configuration. Do not add Cloudflare credentials to this directory.

After deployment, bind the Worker to a custom domain that you control.
