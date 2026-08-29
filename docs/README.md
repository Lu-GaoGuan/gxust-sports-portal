# 项目文档

此目录用于保存确认后的需求、接口、数据库、部署和内容规范文档。

当前需求来源仍保留在项目根目录的原始 Office 文件中，后续整理时不修改原件。

## 当前阶段

- 第一阶段：迎新展示页面、内容 API、Django Admin 内容管理和审核制留言已实现。前端已接入 REST API，云端使用 Pages Functions + D1，本地可继续使用 Django API。
- 第二阶段：邮箱注册、帖子、评论、举报、管理员扩展、软删除恢复和审计记录尚未实现，需要先确认邮箱验证码、隐私规则和正式部署方案。
- 人物照片、活动照片、视频、学校或学院 Logo、2026 级招新安排须完成内容与授权核验后再由管理后台发布。

## 公开 API

- `GET /api/profile/`：体育部资料。
- `GET /api/members/`：可展示成员。
- `GET /api/activities/`：可展示活动及媒体。
- `GET /api/faqs/`：可展示常见问题。
- `GET /api/messages/`：当前公开且未删除的留言。
- `POST /api/messages/`：提交并立即公开留言，字段为 `nickname` 和 `content`。
- `GET /api/admin/messages/`：管理员读取公开留言，需要 Bearer 口令。
- `DELETE /api/admin/messages/{id}/`：管理员软删除留言，需要 Bearer 口令。
