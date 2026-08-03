# ShortRef

[English](README-en.md) | **简体中文**

ShortRef 是一个小型个人稳定引用服务，可生成如下形式的链接：

```text
https://reference.gany.app/qeoLCypr
```

它有意将私有链接管理与公开跳转路径分离：

```text
本地 WorkBuddy Skill  --写入-->  Cloudflare Workers KV  --读取-->  Cloudflare Worker
       私有记录                     最小映射数据                    302 跳转
```

公开 Worker 不提供创建接口、管理页面、登录系统、Cookie、Session 或 API Token。详细的标题、项目名称、标签、备注和迁移历史均保留在本地 Markdown 与 JSON 文件中。

## 仓库结构

```text
ShortRef/
├── worker/                 Cloudflare Worker；仅支持 GET/HEAD 并读取 KV
├── skill/shortref/         WorkBuddy Skill 与仅使用标准库的 Python CLI
├── docs/                   架构、协议、部署和安全文档
└── .github/workflows/      无第三方依赖的测试工作流
```

## 设计原则

- `reference.gany.app/{id}` 是稳定的公开标识符。
- ID 采用确定性生成：规范化 URL → SHA-256 → Base62 → 8 个字符。
- 发生哈希碰撞时，ID 每次增加一个字符，最长为 12 个字符。
- ID 创建后保持不变，目标地址以后可以迁移。
- 跳转使用 `302` 和 `Cache-Control: no-store`，以便今后修改目标地址。
- Cloudflare KV 仅存储 `{ version, url, status }`。
- 本地数据是描述性元数据和变更历史的权威来源。

## 快速开始

1. 部署 Worker，并创建或绑定其 KV namespace。参见 [`docs/deployment-zhcn.md`](docs/deployment-zhcn.md)。
2. 将 Worker 绑定到 `reference.gany.app`。
3. 在 WorkBuddy 中安装 `skill/shortref`。
4. 将 `skill/shortref/templates/config.example.json` 复制到私有本地路径。
5. 在本地设置 `SHORTREF_CONFIG` 和 `CLOUDFLARE_SHORTREF_TOKEN`。
6. 创建引用：

```bash
python skill/shortref/scripts/shortref.py create "https://example.com/docs" \
  --title "示例文档" \
  --project "示例项目"
```

## 验证

```bash
cd worker
npm run check

cd ..
python -m unittest discover -s skill/shortref/tests -v
```

## 当前定位

当前版本有意保持非常克制。它是个人稳定引用层，而不是面向公众的短链平台。

## 许可证

MIT
