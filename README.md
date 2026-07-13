# wechat-linux-version-tracker

每日自动追踪 Linux 版微信客户端的最新版本号。

通过 GitHub Actions 每天定时探测微信官方安装包的版本，并将结果发布为：

- 一个**网站首页**（`index.html`），展示当前版本与更新时间；
- 一个 **`latest.json`** 文件：`{"currentVersion":"x.x.x.x","updateTime":"ISO8601"}`。

产物统一发布到独立的 **`gh-pages`** 分支（与源码 `main` 分支分离）。

## 工作原理

微信官方 `.deb` 安装包（[WeChatLinux_x86_64.deb](https://dldir1v6.qq.com/weixin/Universal/Linux/WeChatLinux_x86_64.deb)）本质是一个 Unix `ar` 归档，其中第二个成员 `control.tar.*` 保存了 Debian `control` 元数据（含 `Version` 字段）。

[`scripts/detect_version.py`](scripts/detect_version.py) 利用 HTTP Range 请求**只下载 ar 头部和几 KB 的 `control` 成员**（而非整个 ~200MB 安装包），解析出 `Version` 字段。

## 项目结构

| 文件 | 说明 |
| --- | --- |
| `.github/workflows/daily-check.yml` | GitHub Actions 工作流：每日定时 / 手动触发 |
| `scripts/detect_version.py` | 探测微信 `.deb` 的版本号 |
| `scripts/build_site.py` | 生成 `latest.json`（版本未变更时保留原始 `updateTime`） |
| `web/index.html` | 网站首页模板（前端读取 `latest.json` 展示） |

## 工作流逻辑

1. 定时（默认每天 UTC 00:00 / 北京时间 08:00）或手动触发；
2. 运行 `detect_version.py` 探测最新版本；
3. 读取 `gh-pages` 分支已有的 `latest.json`：版本一致则沿用旧 `updateTime`，否则记录当前时间；
4. 将 `index.html` + `latest.json` 发布到 `gh-pages` 分支。

## 启用步骤

1. 将本仓库推送到 GitHub。
2. 在 **Settings → Actions → General → Workflow permissions** 中选择 **Read and write permissions**（工作流需要写权限以推送到 `gh-pages`）。
3. 手动触发一次工作流：**Actions → Daily WeChat Linux Version Check → Run workflow**，生成 `gh-pages` 分支。
4. 在 **Settings → Pages** 中将 **Source** 设为 **Deploy from a branch**，分支选择 **`gh-pages` / `(root)`**。
5. 访问 `https://<用户名>.github.io/<仓库名>/` 查看首页，`.../latest.json` 获取版本数据。
6. 替换 `public/CNAME` 中的域名为自定义域名。

## 本地测试

```bash
python3 scripts/detect_version.py                       # 打印当前版本号
python3 scripts/build_site.py "$(python3 scripts/detect_version.py)" prev.json public/latest.json
```
