# ShortRef Worker

The public half of ShortRef. It performs exactly one operation:

```text
GET /{id} -> read SHORTREF_KV -> 302 redirect
```

There is no public creation endpoint, dashboard, authentication system, cookie, session, or write path.

## Commands

```bash
npm install
npm test
npm run dev
npm run deploy:dry
npm run deploy
```

The first deployment can automatically provision the KV namespace because the binding in `wrangler.jsonc` omits an ID. After deployment, copy the namespace ID from Cloudflare into the local WorkBuddy configuration. Do not add Cloudflare credentials to this directory.

Bind `reference.gany.app` as a Custom Domain in the Cloudflare dashboard after the Worker is deployed.
