# GitHub 驱动的免费/低成本部署

## 方案结论

本项目是 Vue 3 + Django，不需要改写成 React。

| 方案 | Vue 前端 | Django 后台/API | 数据库 | 上传媒体持久化 | 适合场景 |
| --- | --- | --- | --- | --- | --- |
| Cloudflare Pages | 很适合 | 不直接支持传统 Django 服务 | 无 | 无 | 免费、快速的公开展示前端 |
| Vercel | 很适合 | 不建议直接运行当前 Django | 无 | 无 | 前端预览，与 Cloudflare Pages 类似 |
| Render | 支持静态站 | 三者中最适合当前 Django | 可接 PostgreSQL | 免费/临时磁盘不适合长期上传 | 完整功能演示 |

推荐组合：GitHub 保存公开源码，Cloudflare Pages 部署 Vue 前端，Render 部署 Django API 和 PostgreSQL。

Render 免费套餐、数据库免费期限、休眠和额度政策可能变化，应以创建服务时控制台显示为准。免费实例可能休眠，首次请求会较慢；后台新上传媒体若没有对象存储，重部署后可能丢失。仓库内已确认的初始活动媒体可在部署时恢复。

## Cloudflare Pages

在 Cloudflare 控制台连接 GitHub 仓库，创建 Pages 项目：

- Framework preset：Vue 或 Vite。
- Root directory：仓库根目录。
- Build command：`npm --prefix frontend ci && npm --prefix frontend run build`
- Build output directory：`frontend/dist`
- Runtime environment variable：`RENDER_API_ORIGIN=https://你的-render-api域名`

仓库内的 Pages Function 会把同域 `/api/*` 请求转发到 Render。前端生产构建默认使用 `/api`，浏览器不直接跨域访问 Render，因此无需配置 Cloudflare 域名的 CORS/CSRF 白名单。`RENDER_API_ORIGIN` 只填写 HTTPS 域名，不包含 `/api`，并同时配置到 Production 和 Preview 环境。

## Render Django API

仓库根目录包含 `render.yaml`。在 Render 选择 Blueprint/从 GitHub 创建服务并选中此仓库。

Render 自动提供 `RENDER_EXTERNAL_HOSTNAME`，Django 会将其加入 `ALLOWED_HOSTS`。Blueprint 不再要求填写 Cloudflare 的 CORS/CSRF 白名单。部署自动安装依赖、执行数据库迁移、收集静态文件，并在数据库为空时导入初始内容。

创建管理员可在 Render Shell 执行：

```bash
python manage.py createsuperuser
```

不要在公开日志、仓库或聊天中提供管理员密码和环境变量值。

## Vercel 备选

- Build command：`npm --prefix frontend ci && npm --prefix frontend run build`
- Output directory：`frontend/dist`
- Environment variable：`VITE_API_BASE_URL=https://你的-render-api域名/api`

对本项目而言，Cloudflare Pages 和 Vercel 都只负责前端。Cloudflare Pages作为当前首选，Vercel 可作为备选预览环境。
