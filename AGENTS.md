# AGENTS.md

本文件是本项目后续开发、维护和协作的统一规范。除用户在当前任务中明确提出的新要求外，所有开发工作均应遵守本文件。

## 1. 项目目标与定位

- 项目名称：广西科技大学电子工程学院团委学生会体育部迎新网站。
- 运营与备案主体：广西科技大学电子工程学院。
- 当前主要受众：2026级新生，以及希望了解电子工程学院团委学生会体育部的在校学生。
- 第一阶段定位：完成体育部宣传、迎新、招新、历届传承、现任团队、活动风采和常见问题等内容展示。
- 第二阶段定位：提供邮箱注册、帖子、评论、举报和管理员审核功能；社区内容采用先审后发，删除内容应支持恢复并保留操作记录。
- 网站首先是可直接使用的迎新与招新平台，不制作与实际业务无关的营销落地页。

## 2. 技术结构

### 前端

- 使用 Vue 3、Vite、Vue Router 和 Axios。
- 前端目录为 `frontend/`。
- 页面通过 Axios 调用后端 REST API，不直接访问数据库。
- API 基础地址由 `VITE_API_BASE_URL` 配置。

### 后端

- 使用 Python、Django、Django REST Framework、django-cors-headers 和 Pillow。
- 后端目录为 `backend/`。
- Django 项目名为 `config`，主要应用名为 `portal`。
- Django Admin 是首期内容管理后台，并使用 django-simpleui 提供管理界面。
- REST API 统一使用 `/api/` 前缀。

### 数据库

- 开发阶段使用 SQLite，数据库文件为 `backend/db.sqlite3`。
- 生产环境数据库方案另行配置，不得把 SQLite 的开发假设写死在业务代码中。
- 所有数据结构变更必须通过 Django migration 管理。

### 前后端关系

```text
Vue 3 前台
    |
    | Axios / REST API
    v
Django REST Framework
    |
    +-- Django Admin + SimpleUI
    +-- SQLite（开发）
    +-- 媒体存储（开发阶段本地，生产方案另行配置）
```

## 3. 目录说明

- `frontend/`：Vue 3 前端源码、路由、API 客户端和构建配置。
- `backend/config/`：Django 全局配置、根路由、WSGI 和 ASGI 入口。
- `backend/portal/`：体育部网站主要业务应用、API、模型、后台注册和测试。
- `backend/requirements.txt`：后端 Python 依赖及固定版本。
- `docs/`：确认后的需求、接口、数据库、内容、隐私和部署文档。
- `assets_raw/`：经确认后归档的原始 Logo、人物照片、活动照片和宣传视频。原始素材不能直接作为公开静态资源使用。
- `部门照片/`：用户提供的部门活动照片和视频，是当前活动素材的主要来源。未经允许不得移动、重命名、覆盖或删除。
- 项目根目录的 DOCX、PPTX、XLSX 等文件：原始需求和历史资料，应保留原件。
- `.env.example`：允许提交的环境变量示例，不得包含真实密码或密钥。

## 4. 常用命令

所有 Python 命令必须明确调用项目虚拟环境，不依赖终端持续处于激活状态。

### 安装后端依赖

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

### Django 系统检查

```powershell
.\.venv\Scripts\python.exe backend\manage.py check
```

### 创建迁移

```powershell
.\.venv\Scripts\python.exe backend\manage.py makemigrations
```

### 执行迁移

```powershell
.\.venv\Scripts\python.exe backend\manage.py migrate
```

### 后端测试

```powershell
.\.venv\Scripts\python.exe backend\manage.py test portal
```

### 启动后端

```powershell
.\.venv\Scripts\python.exe backend\manage.py runserver 127.0.0.1:8000
```

- API 健康检查：`http://127.0.0.1:8000/api/health/`
- Django Admin：`http://127.0.0.1:8000/admin/`

### 安装前端依赖

```powershell
Set-Location frontend
npm install
```

### 启动前端

```powershell
Set-Location frontend
npm run dev
```

- 前端开发地址：`http://127.0.0.1:5173/`

### 前端构建

```powershell
Set-Location frontend
npm run build
```

## 5. 中文命名与编码规范

- 所有新建文本文件统一使用 UTF-8 编码。
- 用户界面、后台字段名称、帮助文本和业务文档默认使用简体中文。
- 中文文案应自然、准确、正式，不使用乱码、网络识别残句或未经校对的 OCR 文本。
- Python、JavaScript、Vue 组件属性、函数、变量、API 字段和数据库字段使用清晰的英文命名。
- Python 遵循 PEP 8，模块和函数使用 `snake_case`，类使用 `PascalCase`。
- JavaScript 使用 `camelCase`，Vue 组件文件使用 `PascalCase.vue`。
- API 路径使用简洁稳定的英文小写形式；JSON 字段保持统一命名风格。
- 不随意重命名用户提供的中文素材文件。代码中如需引用，应通过媒体记录或映射关系处理。
- 新增代码默认使用 ASCII 标点；面向用户的中文内容使用规范中文标点。

## 6. 响应式与可用性要求

- 所有公开页面和 Django 定制管理页面都必须适配手机、平板和电脑。
- 不得只针对单一桌面分辨率开发。
- 页面应在常见窄屏、中等宽度和桌面宽度下保持可读、可操作、无横向溢出。
- 图片和视频必须设置稳定尺寸、宽高比或响应式约束，避免加载时造成布局跳动。
- 文字不得溢出按钮、卡片、导航或其他容器，不得与图片或其他文字重叠。
- 交互控件应具有明确的加载、空数据、错误、禁用和成功状态。
- 每个页面完成后应至少检查手机、平板和桌面三种视口。

## 7. 内容真实性

- 不得编造人物姓名、职务、专业班级、任期、届次、年份、政策、奖学金金额、二课学分、综测规则或活动资料。
- 只有用户明确确认或原始资料能够可靠证明的内容才能进入正式页面和数据库。
- 无法确认的内容应标记为待确认、暂不展示，或使用中性占位文案。
- 学院2026年综合测评文件包含“意见征求稿”标识。没有正式发布版时，只能谨慎引用稳定内容，并注明以学校和学院当学期正式通知为准。
- 政策类信息必须记录来源文件、适用对象、生效时间和最后核验时间。
- 不得根据照片自行判断人物姓名、关系、职务、活动日期或活动结果。
- 内部预算、考勤、老师联系方式、执行分工和私人名单不得默认公开。

## 8. 图片与视频规范

- 缺少人物照片、活动封面或视频封面时，统一使用明确标注的占位图，不得使用无关人物照片代替。
- 占位图应显示“照片待补充”“视频待补充”等明确文字，不伪装成真实素材。
- 原始素材不得直接覆盖；裁剪、压缩、转码后的文件应作为派生文件单独保存。
- 使用素材前应核对活动分类、清晰度、重复文件、公开范围和肖像授权。
- `部门照片/` 中的素材可用于候选筛选，但私人聚会、个人单人照、群聊截图或可能引起误解的照片不得默认发布。
- 相同图片只保留一个公开版本，原始重复文件仍不得擅自删除。
- 图片应提供有意义的替代文本；视频应提供封面、标题和必要的说明。

## 9. 测试与验证

- 每次修改后必须运行与修改范围相关的测试或验证。
- 后端代码、模型、路由或配置发生变化时，至少运行：

```powershell
.\.venv\Scripts\python.exe backend\manage.py check
.\.venv\Scripts\python.exe backend\manage.py test portal
```

- 数据模型发生变化时，还必须运行迁移检查并执行迁移：

```powershell
.\.venv\Scripts\python.exe backend\manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe backend\manage.py migrate
```

- 前端代码发生变化时，至少运行：

```powershell
Set-Location frontend
npm run build
```

- 涉及前后端联调时，应启动两端并验证实际 HTTP 响应、API 数据和 CORS。
- 涉及页面布局时，应检查手机、平板和桌面视口。
- 仅修改 Markdown 等文档时，可以不运行完整代码测试，但必须检查文件存在、内容完整、命令与当前项目一致。
- 不得把“命令未运行”描述为“测试通过”；无法运行的验证必须在交付说明中明确指出。

## 10. 修改范围与素材保护

- 未经用户明确允许，不得删除、移动、重命名、压缩或覆盖用户提供的照片、视频、Office 文件和其他原始资料。
- 不得重写与当前任务无关的文件，不得顺手进行无关重构。
- 发现用户在工作期间新增或修改的文件时，应保留并与其协同，不得回退。
- 修改已有文件前应先阅读其当前内容，保持项目既有结构和命名习惯。
- 删除生成文件前必须确认目标绝对路径位于项目工作区内。
- 不得使用破坏性 Git 或文件系统命令处理未确认的用户内容。

## 11. 密钥与正式环境配置

- 密码、Django 正式 `SECRET_KEY`、邮箱密码、云服务密钥、数据库密码、对象存储密钥和验证码服务凭据不得写入代码仓库。
- 正式配置通过环境变量或部署平台的密钥管理功能提供。
- `.env`、本地数据库、上传媒体、构建产物和虚拟环境必须保持在 `.gitignore` 中。
- `.env.example` 只能包含字段名和无敏感性的示例值。
- 不得在日志、测试输出、截图、README 或提交记录中泄露真实凭据。
- Django Admin 超级管理员由学院指定人员创建和管理，不在初始化代码中预置账号或密码。

## 12. 任务完成汇报

每次任务完成后必须向用户说明：

- 修改、创建或删除了哪些文件。
- 实现了哪些行为或功能。
- 运行了哪些检查、测试、迁移、构建或启动命令。
- 每项验证的实际结果。
- 是否修改了数据库结构或写入了业务数据。
- 当前仍存在的遗留问题、待确认资料或无法完成的验证。
- 若开发服务器仍在运行，应提供访问地址；若未启动，也应明确说明。

不得只回复“已完成”，也不得隐瞒失败的命令、未运行的测试或尚未解决的问题。
