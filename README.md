# 把画面说给 AI 听 · 网页版

静态网页：输入词条关键词（中文/英文/俗称），带出中英文提示词，配图缩略图 + 一键复制。

## 文件

- `index.html` — 单页应用（无依赖，纯 HTML/CSS/JS）
- `data.json` — 112 条词条数据（名称/别名/中英提示词/章节/配图路径）
- `images/` — 112 张配图（压缩后）
- `build_web.py`（上级目录）— 从章节 Markdown 重新生成数据和图片

## 本地预览

由于网页用 `fetch` 加载 `data.json`，需要用本地服务器打开（不能直接双击 file://）：

```bash
cd site
python3 -m http.server 8000
# 打开 http://localhost:8000
```

## GitHub Pages 部署

1. 在 GitHub 新建一个仓库（如 `picture-dictionary`）
2. 把本目录（`site/`）所有内容推送到仓库根目录或 `docs/` 目录
3. 仓库 Settings → Pages → Source 选 `main` 分支根目录（或 `/docs`）
4. 访问 `https://<用户名>.github.io/<仓库名>/`

命令行示例（需已配置 GitHub 认证）：

```bash
cd site
git init
git add .
git commit -m "init picture dictionary"
git branch -M main
git remote add origin https://github.com/<用户名>/<仓库名>.git
git push -u origin main
```

## 重新生成数据

词条文字改动后：

```bash
cd 项目根目录
python3 build_web.py   # 重新提取 data.json + 复制图片到 site/images/
```
