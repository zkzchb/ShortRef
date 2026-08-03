# ShortRef Worker

[English](README.md) | **简体中文**

这是 ShortRef 的公开端，对外提供三类响应：

```text
GET /       -> 200 服务说明页
GET /{id}  -> 读取 SHORTREF_KV -> 302 跳转
其他路径     -> 404 引用错误页
```

它不提供公开创建接口、管理面板、身份验证系统、Cookie、Session 或任何写入路径。服务说明页与 404 页面均为通用内容，不包含任何特定部署域名。

## 静态页面

```text
public/
├── index.html
└── 404.html
```

`wrangler.jsonc` 将该目录配置为名为 `ASSETS` 的静态资源绑定，并启用 `run_worker_first: true`。因此所有请求都会先进入 Worker，再由 Worker 通过 `env.ASSETS` 读取相应页面。Worker 代码和页面会通过同一条部署命令一起发布。

## 命令

```bash
npm install
npm test
npm run dev
npm run deploy:dry
npm run deploy
```

由于 `wrangler.jsonc` 中的绑定未填写 ID，首次部署时 Wrangler 可以自动创建 KV namespace。部署完成后，将 Cloudflare 中的 namespace ID 复制到本地 WorkBuddy 配置中。不要把 Cloudflare 凭据放入本目录。

部署完成后，将 Worker 绑定到你自己控制的 Custom Domain。
