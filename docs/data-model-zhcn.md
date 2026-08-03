# 数据模型

[English](data-model.md) | 简体中文

## 远程 KV 记录

线上只保存跳转所必需的数据：

```json
{
  "version": 1,
  "url": "https://example.com/docs-v2",
  "status": "active"
}
```

- `version`：远程数据结构版本。
- `url`：当前跳转目标。
- `status`：取值为 `active` 或 `inactive`。

## 本地索引

`index.json` 是供本地程序读取的记录。它保存每个 ID、原始来源 URL、当前目标地址、本地元数据、时间戳和历史记录。

迁移后，原始 `source_url` 保持不变；`target_url` 表示当前目标地址。

## 本地 Markdown

每条引用还对应一个 `records/{id}.md` 文件。Markdown 根据本地索引生成，供人阅读。它可以保存标题、项目、标签、备注、用途、使用位置以及目标迁移历史等私有上下文信息。

本地数据目录有意放在本仓库之外，不应公开同步。

## 备份

每次修改本地数据前，ShortRef 都会把现有索引复制到 `backups/`。保留的备份数量由 `storage.backup_limit` 控制。
