# 公开 REST API

开发环境基础地址：`http://127.0.0.1:8000/api`。所有请求和响应均使用 JSON；图片与视频字段返回可直接访问的绝对 URL。

公开内容只能使用 `GET` 查询。成员、活动和 FAQ 的新增、修改、删除必须通过 Django Admin 完成。留言只允许公开查询和匿名提交。

## 部门资料

`GET /profile/`

无需参数。尚未创建资料时返回 `null`。

```json
{
  "introduction": "体育部简介",
  "welcome_slogan": "迎新标语",
  "recruitment_info": "招新信息",
  "contact_info": "公开联系方式",
  "qq_group_qr_code": "http://127.0.0.1:8000/media/department/qr_codes/example.png",
  "updated_at": "2026-08-28T20:00:00+08:00"
}
```

## 历届成员

- `GET /members/`：返回全部允许展示的成员。
- `GET /members/{id}/`：返回指定允许展示的成员；记录不存在或被隐藏时返回 `404`。
- `GET /members/current/`：以允许展示成员中的最大届数作为当前届，只返回该届成员。

```json
[
  {
    "id": 1,
    "name": "示例姓名",
    "major_class": "示例专业班级",
    "position": "部长",
    "generation": 6,
    "tenure": "2026-2027",
    "introduction": "个人介绍",
    "welcome_message": "新生寄语",
    "photo": "http://127.0.0.1:8000/media/members/example.jpg"
  }
]
```

## 活动

- `GET /activities/`：返回全部允许展示的活动。
- `GET /activities/{id}/`：返回活动详情和关联媒体；记录不存在或被隐藏时返回 `404`。

```json
{
  "id": 1,
  "name": "示例活动",
  "category": "sports",
  "category_label": "体育赛事",
  "activity_date": "2026-08-28",
  "introduction": "活动简介",
  "cover": "http://127.0.0.1:8000/media/activities/covers/example.jpg",
  "media": [
    {
      "id": 1,
      "file": "http://127.0.0.1:8000/media/activities/media/example.mp4",
      "media_type": "video",
      "description": "活动视频"
    }
  ]
}
```

## 常见问题

`GET /faqs/`

只返回允许展示的 FAQ。

```json
[{"id": 1, "question": "示例问题？", "answer": "示例回答。"}]
```

## 留言

### 查询公开留言

`GET /messages/`

只返回当前公开且未被管理员软删除的留言。

```json
[
  {
    "id": 1,
    "nickname": "同学",
    "content": "留言内容",
    "submitted_at": "2026-08-28T20:00:00+08:00"
  }
]
```

### 提交留言

`POST /messages/`

请求字段：

| 字段 | 类型 | 必填 | 规则 |
| --- | --- | --- | --- |
| `nickname` | string | 是 | 去除首尾空白后为 1–50 个字符 |
| `content` | string | 是 | 去除首尾空白后为 2–1000 个字符，不允许非法控制字符 |

```json
{"nickname": "新生", "content": "想了解体育部招新安排。"}
```

成功返回 `201 Created`，新留言立即公开。默认按来源 IP 限制为每小时 5 次，超过限制返回 `429 Too Many Requests`；Django 本地后端可通过环境变量 `MESSAGE_SUBMISSION_RATE` 调整。

Cloudflare 云端提供受 `ADMIN_API_TOKEN` 保护的管理接口：

- `GET /admin/messages/`：读取当前公开留言。
- `DELETE /admin/messages/{id}/`：软删除指定留言并写入操作记录。

管理员页面地址为 `/admin-comments`，不会在公共导航中显示。

校验失败返回 `400 Bad Request`：

```json
{"content": ["留言内容至少需要 2 个字符。"]}
```

## 跨域

开发环境允许 `http://127.0.0.1:5173` 和 `http://localhost:5173`。生产环境通过 `CORS_ALLOWED_ORIGINS` 配置实际前端域名，不应使用全域允许配置。
