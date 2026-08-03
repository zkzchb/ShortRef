# 安全模型

[English](security.md) | 简体中文

## 公开访问面

公开服务仅支持：

```text
GET  /{8-12 位 Base62 ID}
HEAD /{8-12 位 Base62 ID}
```

不存在公开写入 API 或管理界面。其他路径均返回 `404`，其他方法均返回 `405`。

## Cloudflare 凭据

应使用专用 Cloudflare API Token，而不是 Global API Key。

建议权限范围：

- 权限：**Workers KV Storage Write**；
- 资源：仅限相关 Cloudflare 账户；
- 除非部署另有需要，否则不授予 Zone 编辑、DNS 编辑、Worker 编辑或全局账户权限。

Token 只能保存在 `cloudflare.api_token_env` 指定的环境变量中。示例使用 `CLOUDFLARE_SHORTREF_TOKEN`。

## 隐私边界

目标 URL 不是秘密。任何知道或猜到 ShortRef ID 的人都可以解析该链接。不要使用 ShortRef 保存包含凭据、私有访问 Token、签名密钥或敏感查询参数的 URL。

本地工具会拒绝 URL 中直接嵌入的用户名或密码，但无法可靠识别查询参数中的所有秘密信息。

## “只读”的准确含义

Cloudflare 不为 Worker 内部的 KV binding 提供单独的只读模式。已部署代码之所以只读，是因为它只包含 `get()`，并且没有暴露写入路径。因此，仍必须妥善保护 GitHub 仓库、Cloudflare 账户和部署权限。

## 跳转策略

- 仅接受 `http` 和 `https` 目标地址。
- 停用或格式错误的记录返回 `404`。
- 跳转使用 `302`，而不是 `301`。
- 响应使用 `Cache-Control: no-store`，以保留未来迁移目标地址的控制权。
- Worker 应用代码不记录目标 URL。
