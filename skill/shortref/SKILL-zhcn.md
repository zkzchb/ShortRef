---
name: shortref
description: 在本地创建和维护私有 ShortRef 记录，同时只向 Cloudflare Workers KV 发布最小跳转映射。
---

# ShortRef

[English](SKILL.md) | 简体中文

当用户要求创建、查看、迁移、停用、启用、验证或同步 `reference.gany.app` 下的 ShortRef 链接时，使用本 Skill。

## 安全边界

- Cloudflare Worker 在代码层面只读，不提供公开写入接口。
- 仅通过本地机器上的 `scripts/shortref.py` 写入 KV。
- 不得将 Cloudflare Token 写入本 Skill、Git、Markdown 或 `config.json`。
- Token 必须从 `cloudflare.api_token_env` 指定的环境变量中读取。
- 详细的标题、项目、标签、备注和历史记录仅保存在配置指定的本地数据目录中。
- 不要缩短包含秘密、凭据或访问 Token 的 URL。跳转目标并不私密。

## 配置

按以下顺序查找配置：

1. `--config PATH`
2. `SHORTREF_CONFIG`
3. `~/.shortref/config.json`

首次使用前，将 `templates/config.example.json` 复制到 Skill 目录之外，并填写 Cloudflare 账户 ID、KV namespace ID、基础 URL 和本地数据目录。

## 操作

创建确定性引用：

```bash
python scripts/shortref.py create "<URL>" --title "<TITLE>" --project "<PROJECT>" --tag "<TAG>" --notes "<NOTES>"
```

在不改变引用 ID 的情况下修改目标地址：

```bash
python scripts/shortref.py update <ID> "<NEW_URL>" --reason "<REASON>"
```

停用或启用：

```bash
python scripts/shortref.py disable <ID> --reason "<REASON>"
python scripts/shortref.py enable <ID> --reason "<REASON>"
```

查看和列出：

```bash
python scripts/shortref.py show <ID>
python scripts/shortref.py list
```

验证或修复同步状态：

```bash
python scripts/shortref.py verify [ID]
python scripts/shortref.py sync [ID]
python scripts/shortref.py sync [ID] --apply
```

在允许 `sync` 修改 KV 前，必须先不带 `--apply` 运行一次。完成后报告生成的短链，并说明本次操作是创建、复用、更新还是同步了记录。
