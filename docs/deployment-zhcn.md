# 部署

[English](deployment.md) | **简体中文**

## 1. 部署 Worker

在 Worker 目录中执行：

```bash
cd worker
npm install
npx wrangler login
npm run deploy:dry
npm run deploy
```

同一次 Wrangler 部署会同时上传 Worker 代码和 `worker/public/` 中的两个通用 HTML 页面。它们通过 `ASSETS` binding 提供给 Worker，不需要另外创建 Cloudflare Pages 项目。

`wrangler.jsonc` 中定义了未填写 namespace ID 的 `SHORTREF_KV` binding。首次使用 Wrangler 部署时，Cloudflare 可以自动创建 namespace，并更新本地配置。你也可以手动创建 KV namespace，然后把 ID 添加到 binding 中：

```jsonc
"kv_namespaces": [
  {
    "binding": "SHORTREF_KV",
    "id": "YOUR_NAMESPACE_ID"
  }
]
```

## 2. 绑定自定义域名

在 Cloudflare Workers & Pages 中：

1. 打开 `shortref` Worker。
2. 进入 **Settings → Domains & Routes**。
3. 添加 Custom Domain：`reference.gany.app`。
4. 确认域名状态为 active。

## 3. 创建本地 Token

在 Cloudflare 中创建一个专用 API Token，仅为相关账户授予 **Workers KV Storage Write** 权限。记录账户 ID 和 ShortRef KV namespace ID。不要使用 Global API Key。

## 4. 配置本地 Skill

将 `skill/shortref/templates/config.example.json` 复制到私有本地目录，然后填写本地数据目录、账户 ID、namespace ID 和 Token 环境变量名称。

PowerShell 示例：

```powershell
$env:SHORTREF_CONFIG = "D:\ShortRef\config.json"
$env:CLOUDFLARE_SHORTREF_TOKEN = "your-token"
```

## 5. 端到端测试

```powershell
python .\skill\shortref\scripts\shortref.py create `
  "https://example.com/docs" `
  --title "示例文档"
```

打开返回的 `https://reference.gany.app/{id}`。由于 KV 采用最终一致性，新的或已修改的值可能需要一段时间才会在 Cloudflare 的所有地区可见。

## 更新代码

```bash
cd worker
npm run check
npm run deploy:dry
```

Worker 运行时不需要 Cloudflare API Token。它的运行时绑定包括：用于跳转映射的 `SHORTREF_KV`，以及用于通用服务页和 404 页面的 `ASSETS`。
