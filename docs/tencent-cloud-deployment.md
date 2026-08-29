# 腾讯云部署指南（新手版）

本文档适用于本项目当前的第一阶段网站。生产架构为：

```text
浏览器
  ↓ HTTP / HTTPS
Nginx（Vue 前端、媒体、静态文件、反向代理）
  ↓
Gunicorn + Django REST Framework
  ↓
MySQL 8.4（仅 Docker 内网访问）
```

## 1. 需要准备什么

- 一个完成实名认证的腾讯云账号。
- 一台腾讯云轻量应用服务器。
- 可选：域名。中国大陆服务器对外使用域名时通常需要完成ICP备案。
- 可选：腾讯云 SSL 证书。公网 IP 测试阶段可以先使用 HTTP。

推荐服务器配置：

- 地域：主要访问者在广西时，优先选择中国大陆南方地域；如果暂时不准备备案，可先选择中国香港用于测试。
- 系统：Ubuntu 24.04 LTS 64 位。
- 配置：2 核 2 GB 可起步，2 核 4 GB 更稳妥。
- 系统盘：至少 40 GB。
- 公网带宽：视频较多，建议至少 5 Mbps；正式使用时建议迁移视频到腾讯云 COS/CDN。

购买价格、可选地域、备案和免费证书政策会变化，请以腾讯云控制台当时显示为准。

如果购买 2 GB 内存实例，应在服务器配置约 2 GB Swap，并将 `.env.production` 中的 `GUNICORN_WORKERS` 改为 `2`。4 GB 内存实例可保持默认值 `3`。当前项目不需要 8 GB 内存。

## 2. 创建服务器

1. 登录腾讯云控制台，搜索“轻量应用服务器”。
2. 新建实例，选择 Ubuntu 24.04 LTS，不选择带第三方网站程序的镜像。
3. 设置一个强登录密码，或按控制台指引配置 SSH 密钥。
4. 在防火墙/安全组中仅开放：
   - `22/TCP`：SSH 管理，条件允许时限制为自己的公网 IP。
   - `80/TCP`：HTTP。
   - `443/TCP`：HTTPS。
5. 不要开放 `3306`、`8000`、`5173`；MySQL、Django 和 Vite 不应直接暴露公网。
6. 记录服务器公网 IP。

## 3. 第一次连接服务器

Windows PowerShell 执行：

```powershell
ssh root@服务器公网IP
```

如果服务器默认使用 `ubuntu` 用户，则执行：

```powershell
ssh ubuntu@服务器公网IP
```

首次连接会询问是否信任主机指纹。应先在腾讯云控制台核对实例信息，再输入 `yes`。

## 4. 安装 Docker

在服务器中执行腾讯云/Ubuntu 官方当前推荐的 Docker 安装流程。安装完成后验证：

```bash
docker --version
docker compose version
```

如果当前登录用户不是 root，需要将用户加入 Docker 组，重新登录后再继续：

```bash
sudo usermod -aG docker "$USER"
```

Docker 组近似拥有 root 权限，不要将不可信用户加入该组。

## 5. 在本机生成安全部署包

在项目根目录打开 PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\scripts\package.ps1
```

生成：

- `sports-portal-deploy.tar.gz`
- `sports-portal-deploy.tar.gz.sha256`

部署包不会包含：

- `.env` 或 `.env.production`
- SQLite 数据库
- Python 虚拟环境和 `node_modules`
- `部门照片/` 原始素材
- DOCX、XLSX、PPTX、PDF 原始资料
- 浏览器缓存、测试日志和参考工程

## 6. 上传部署包

本机 PowerShell 执行：

```powershell
scp .\sports-portal-deploy.tar.gz root@服务器公网IP:/opt/
scp .\sports-portal-deploy.tar.gz.sha256 root@服务器公网IP:/opt/
```

服务器执行：

```bash
cd /opt
sha256sum -c sports-portal-deploy.tar.gz.sha256
mkdir -p /opt/sports-portal
tar -xzf sports-portal-deploy.tar.gz -C /opt/sports-portal
cd /opt/sports-portal
```

校验必须显示 `OK`。如果失败，应重新上传，不要继续部署。

## 7. 创建生产环境配置

服务器执行：

```bash
cd /opt/sports-portal
cp .env.production.example .env.production
chmod 600 .env.production
```

生成随机密钥和密码：

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

至少生成三个互不相同的随机值，分别填写：

- `DJANGO_SECRET_KEY`
- `DB_PASSWORD`
- `DB_ROOT_PASSWORD`

编辑文件：

```bash
nano .env.production
```

公网 IP 测试阶段需要替换：

```dotenv
DJANGO_ALLOWED_HOSTS=服务器公网IP
CSRF_TRUSTED_ORIGINS=http://服务器公网IP
```

安全项暂时保持 HTTP 测试值：

```dotenv
DJANGO_SECURE_SSL_REDIRECT=false
DJANGO_SESSION_COOKIE_SECURE=false
DJANGO_CSRF_COOKIE_SECURE=false
DJANGO_SECURE_HSTS_SECONDS=0
```

不要通过微信、QQ 或截图发送 `.env.production` 的内容。

## 8. 首次启动

服务器执行：

```bash
chmod +x deploy/scripts/*.sh
./deploy/scripts/first-deploy.sh /opt/sports-portal
```

该脚本会：

1. 校验 Compose 配置。
2. 构建前后端镜像。
3. 启动 MySQL、Django/Gunicorn 和 Nginx。
4. 执行数据库迁移和静态文件收集。
5. 仅在数据库为空时导入已确认的初始内容。

查看状态和日志：

```bash
docker compose --env-file .env.production ps
docker compose --env-file .env.production logs --tail=200
```

访问：

- 网站：`http://服务器公网IP/`
- 健康检查：`http://服务器公网IP/api/health/`
- 后台：`http://服务器公网IP/admin/`

## 9. 创建管理员

管理员账号不随部署包上传。在服务器执行：

```bash
docker compose --env-file .env.production exec web python manage.py createsuperuser
```

使用学院指定的账号信息和强密码。创建完成后登录 `/admin/`，检查成员、活动、FAQ 和留言。

## 10. 域名、备案与 HTTPS

### 中国大陆服务器

正式使用域名前，通常需要：

1. 购买或准备域名。
2. 在腾讯云完成ICP备案。
3. 备案通过后，在 DNSPod/腾讯云 DNS 中添加 A 记录，指向服务器公网 IP。
4. 申请腾讯云 SSL 证书并完成域名验证。

备案主体、网站名称和页面底部主体信息应与学院授权及实际运营主体一致。上线前应由学院确认备案与内容发布责任。

### 配置 HTTPS

1. 从腾讯云证书控制台下载 Nginx 格式证书。
2. 在服务器创建：

```bash
mkdir -p /opt/sports-portal/deploy/certs
chmod 700 /opt/sports-portal/deploy/certs
```

3. 将证书链保存为 `deploy/certs/fullchain.pem`，私钥保存为 `deploy/certs/privkey.pem`。
4. 复制 HTTPS 模板并替换域名：

```bash
cp deploy/nginx/https.conf.example deploy/nginx/https.conf
nano deploy/nginx/https.conf
```

5. 修改 `.env.production`：

```dotenv
DJANGO_ALLOWED_HOSTS=你的域名
CSRF_TRUSTED_ORIGINS=https://你的域名
DJANGO_SECURE_SSL_REDIRECT=true
DJANGO_SESSION_COOKIE_SECURE=true
DJANGO_CSRF_COOKIE_SECURE=true
DJANGO_SECURE_HSTS_SECONDS=3600
```

6. 验证配置并启动 HTTPS：

```bash
docker compose --env-file .env.production -f docker-compose.yml -f docker-compose.https.yml config >/dev/null
docker compose --env-file .env.production -f docker-compose.yml -f docker-compose.https.yml up -d --build
```

7. 确认 HTTPS、后台登录和所有媒体正常后，再逐步将 HSTS 提高到长期值。不要在证书和所有子域名未确认前启用 HSTS preload。

## 11. 日常更新

上传并解压新版部署包，保留服务器上的 `.env.production` 和证书，然后执行：

```bash
./deploy/scripts/update.sh /opt/sports-portal
```

更新前必须先备份。

## 12. 备份

执行：

```bash
./deploy/scripts/backup.sh /opt/sports-portal /opt/sports-portal-backups
```

会生成：

- `database.sql`
- `media.tar.gz`

备份不能只留在同一台服务器上，应定期下载到受控存储或上传到私有 COS 存储桶，并设置生命周期与访问权限。

## 13. 常用排查命令

```bash
docker compose --env-file .env.production ps
docker compose --env-file .env.production logs nginx --tail=200
docker compose --env-file .env.production logs web --tail=200
docker compose --env-file .env.production logs db --tail=200
docker compose --env-file .env.production exec web python manage.py check --deploy
```

不要把数据库密码、Django 密钥、证书私钥或完整日志发送到公开聊天中。
