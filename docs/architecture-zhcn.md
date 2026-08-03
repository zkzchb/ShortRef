# 架构

[English](architecture.md) | **简体中文**

## 组件

### 1. 本地 WorkBuddy Skill

本地 Skill 是唯一受支持的写入路径。它负责：

- 规范化原始 URL；
- 计算确定性的 Base62 ID；
- 检查本地数据和远程 KV，避免哈希碰撞；
- 将最小跳转记录写入 KV；
- 将详细的私有元数据写入本地 Markdown 和 JSON；
- 目标地址以后发生变化时仍保留原 ID；
- 验证或修复本地数据与 KV 之间的差异。

本地工具仅使用 Python 标准库。

### 2. Workers KV

KV 是在线映射存储。每个 key 都是一个 ShortRef ID，每个 value 都是一个最小 JSON 对象：

```json
{
  "version": 1,
  "url": "https://example.com/docs",
  "status": "active"
}
```

标题、项目、标签、备注、来源说明和历史记录均不会上传。

### 3. Cloudflare Worker

Worker 只接受 `GET` 和 `HEAD`：

- `/` 返回通用服务说明页，状态码为 `200`；
- 有效且启用的 ID 会读取一个 KV key，并返回 `302` 跳转；
- 格式错误、不存在、已停用或记录无效的引用返回通用页面，状态码为 `404`。

两个 HTML 页面位于 `worker/public/`，并作为名为 `ASSETS` 的静态资源绑定随 Worker 一起部署。`run_worker_first: true` 保证 Worker 始终控制路由，再通过 `env.ASSETS` 明确选择需要返回的页面。

Worker 源码中不包含 `put`、`delete` 或 `list` 调用，也不暴露任何写入路由。Cloudflare KV binding 在技术上具备写入能力，因此这里的只读边界由代码保证，而不是由 Cloudflare 提供独立的只读 binding 类型。

## 数据流

```text
创建
URL -> 规范化 -> 哈希 -> 碰撞检查 -> KV PUT -> 本地索引 + Markdown

解析
GET /{id} -> 验证 ID -> KV GET -> 验证目标 -> 302 Location

页面
GET / -> Worker -> ASSETS/index.html -> 200
无效引用 -> Worker -> ASSETS/404.html -> 404

迁移
本地更新 -> 在同一 ID 下执行 KV PUT -> 追加本地历史
```

## 故障处理

- 未知、停用、格式错误或无效的记录返回通用 HTML 页面，同时保持 `404` 状态码。
- 不支持的 HTTP 方法返回 `405`。
- KV 或页面资源读取失败时返回 `503`，并附带简短的重试提示。
- 跳转与 HTML 响应均使用 `Cache-Control: no-store`。
- KV 采用最终一致性，因此新的或已修改的映射可能需要一段时间才会在所有地区生效。
