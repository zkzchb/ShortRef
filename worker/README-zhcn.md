# ShortRef Worker

[English](README.md) | 简体中文

这是 ShortRef 的公开端，只执行一项操作：

```text
GET /{id} -> 读取 SHORTREF_KV -> 302 跳转
```

它不提供公开创建接口、管理面板、身份验证系统、Cookie、Session 或任何写入路径。

## 命令

```bash
npm install
npm test
npm run dev
npm run deploy:dry
npm run deploy
```

由于 `wrangler.jsonc` 中的绑定未填写 ID，首次部署时 Wrangler 可以自动创建 KV namespace。部署完成后，将 Cloudflare 中的 namespace ID 复制到本地 WorkBuddy 配置中。不要把 Cloudflare 凭据放入本目录。

Worker 部署完成后，在 Cloudflare 控制台中将 `reference.gany.app` 绑定为 Custom Domain。
