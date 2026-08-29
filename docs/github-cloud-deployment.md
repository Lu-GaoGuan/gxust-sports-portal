# GitHub 驱动的 Cloudflare 免费部署

## 当前方案

项目的当前云端架构为：

```text
GitHub 公开仓库
    |
    v
Cloudflare Pages（Vue 静态前端）
    |
    +-- Pages Functions（同域 /api/*）
    |
    +-- Cloudflare D1（持久数据）
```

该方案不使用 Render，不需要 PostgreSQL、跨域白名单或银行卡。Cloudflare 免费额度和政策可能调整，应以控制台当前显示为准。Django 后端继续保留，供本地内容管理、测试和导出 D1 初始数据使用。

## 已创建资源

- GitHub 仓库：`Lu-GaoGuan/gxust-sports-portal`
- D1 数据库：`gxust-sports-portal-db`
- D1 绑定名：`DB`
- Pages 构建输出：`frontend/dist`

`wrangler.toml` 已记录 D1 数据库绑定。不要把令牌、密码或其他真实凭据提交到仓库。

## 初始化 D1

在项目根目录执行：

```powershell
npx --yes wrangler@latest login
npx --yes wrangler@latest d1 migrations apply gxust-sports-portal-db --remote
```

`migrations/0001_initial.sql` 创建数据表，`migrations/0002_seed.sql` 导入已确认的初始内容。后续新增迁移后再次运行同一条 `--remote` 命令即可，Wrangler 只执行尚未应用的迁移。

本地测试使用：

```powershell
npx --yes wrangler@latest d1 migrations apply gxust-sports-portal-db --local
npx --yes wrangler@latest pages dev frontend/dist --ip 127.0.0.1 --port 8788
```

## 创建 Pages 项目

在 Cloudflare 控制台选择 Workers 和 Pages，然后使用 **Pages / 导入现有 Git 仓库**。不要创建 Workers Git Build，也不要配置 `npx wrangler deploy`。

- Framework preset：`Vue` 或 `Vite`
- Root directory：仓库根目录
- Build command：`npm --prefix frontend ci && npm --prefix frontend run build`
- Build output directory：`frontend/dist`
- 部署命令：Pages 项目不填写 `npx wrangler deploy`
- `VITE_API_BASE_URL`：不必填写，生产构建默认使用同域 `/api`

首次创建后，在 Pages 项目的 **Settings > Bindings > D1 database bindings** 中添加：

- Variable name：`DB`
- D1 database：`gxust-sports-portal-db`

Production 和 Preview 环境都应绑定。保存后重新部署，访问 `https://你的-pages-域名/api/health/`，应返回 `status: ok`。

构建时会把 `backend/media/activities/confirmed/` 中已确认公开的派生媒体复制到 Pages 输出目录。原始素材目录和未确认素材不会被移动或修改。

## 评论管理

留言通过内容校验和频率限制后立即公开。管理员可以打开 `/admin-comments`，输入管理口令并软删除不适合公开的评论；删除记录和操作日志继续保留在 D1。

在 Pages 项目的 **Settings > Variables and Secrets** 中添加加密 Secret：

- Name：`ADMIN_API_TOKEN`
- Value：使用密码管理器生成的长随机口令，不得与其他账号密码相同

Production 和 Preview 环境应分别配置。修改 Secret 后重新部署。该口令不要写入 `.env`、截图、聊天、GitHub 或公开日志。

## Render 与 Vercel

Render 不再是当前推荐后端，仓库中的 Django 部署配置仅作回退。Vercel 可部署前端，但不能直接替代当前的 Pages Functions + D1 同域后端，因此当前只使用 Cloudflare。
