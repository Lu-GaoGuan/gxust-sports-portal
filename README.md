# 广西科技大学电子工程学院团委学生会体育部迎新网站

面向 2026 级新生的体育部宣传、迎新与招新网站。前端使用 Vue 3，本地后端使用 Django REST Framework，云端后端使用 Cloudflare Pages Functions + D1。匿名留言提交后立即公开，管理员可在受口令保护的页面软删除。

## 环境

- Python 3.12
- Node.js 24
- Django 6.1
- Django SimpleUI
- Vue 3 + Vite
- SQLite（开发阶段）

## 后端

安装依赖：

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

执行迁移：

```powershell
.\.venv\Scripts\python.exe backend\manage.py migrate
```

启动开发服务器：

```powershell
.\.venv\Scripts\python.exe backend\manage.py runserver 127.0.0.1:8000
```

- API 健康检查：`http://127.0.0.1:8000/api/health/`
- SimpleUI 管理后台：`http://127.0.0.1:8000/admin/`

公开接口包括 `/api/profile/`、`/api/members/`、`/api/activities/`、`/api/faqs/` 和 `/api/messages/`。留言提交后立即公开，并保留内容校验和提交频率限制。

项目暂未创建超级管理员。需要时运行：

```powershell
.\.venv\Scripts\python.exe backend\manage.py createsuperuser
```

## 前端

```powershell
Set-Location frontend
npm install
npm run dev
```

开发地址：`http://127.0.0.1:5173/`

前端已接入后端 REST API，包含首页、部门介绍、历届风采、现任成员、活动回顾、新生问答和留言交流七个路由页面。活动图库按媒体真实宽高完整展示，不裁切图片。

## 配置

环境变量示例见 `.env.example`。开发环境有可运行的默认值，生产部署前必须配置正式密钥、域名、邮件服务、数据库和对象存储。

## 测试

```powershell
.\.venv\Scripts\python.exe backend\manage.py test portal
Set-Location frontend
npm run build
```

## 云端部署

- 当前免费方案：Cloudflare Pages（Vue 前端）+ Pages Functions（REST API）+ D1（持久数据）。
- 生产前端通过同域 `/api/` 访问 Functions，无需 Render、PostgreSQL、跨域白名单或银行卡。
- Django + SQLite 保留用于本地内容管理、测试和数据导出，不是当前云端运行依赖。
- 正式长期运行：腾讯云轻量服务器或其他具备持久数据库与对象存储的环境。

部署说明：

- `docs/github-cloud-deployment.md`
- `docs/tencent-cloud-deployment.md`

`.env`、本地数据库、原始 Office/PDF、原始素材目录和管理员凭据不会提交到公开仓库。仓库内的 `backend/media/activities/confirmed/` 是活动页使用的公开派生素材。
