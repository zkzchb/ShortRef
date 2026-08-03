# ShortRef WorkBuddy Skill

[English](README.md) | 简体中文

本目录可以安全地作为 WorkBuddy Skill 安装或复制。目录中不包含个人配置、API Token 或私有链接记录。

## 本地设置

1. 将 `templates/config.example.json` 复制到私有位置。
2. 设置其中的 `data_dir`、Cloudflare 账户 ID 和 KV namespace ID。
3. 创建 Cloudflare API Token，仅为相关账户授予 **Workers KV Storage Write** 权限。
4. 将 Token 保存到环境变量 `CLOUDFLARE_SHORTREF_TOKEN` 中。
5. 将 `SHORTREF_CONFIG` 设置为私有配置文件的路径。

PowerShell 示例：

```powershell
$env:SHORTREF_CONFIG = "D:\ShortRef\config.json"
$env:CLOUDFLARE_SHORTREF_TOKEN = "your-token"
python .\scripts\shortref.py create "https://example.com/docs" --title "示例文档"
```

## 本地数据

脚本会创建：

```text
ShortRefData/
├── index.json
├── records/
│   └── Ab12Cd34.md
└── backups/
    └── index-*.json
```

`index.json` 是本地工具使用的机器可读数据源。Markdown 文件是供人阅读的私有记录。KV 只接收 `version`、`url` 和 `status`。
