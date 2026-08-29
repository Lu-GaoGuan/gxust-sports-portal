const JSON_HEADERS = {
  'Cache-Control': 'no-store',
  'Content-Type': 'application/json; charset=utf-8',
}

const MEMBER_COLUMNS = [
  'id',
  'name',
  'major_class',
  'position',
  'generation',
  'tenure',
  'introduction',
  'welcome_message',
  'photo',
].join(', ')

const ACTIVITY_COLUMNS = [
  'id',
  'name',
  'category',
  'category_label',
  'activity_date',
  'introduction',
  'cover',
].join(', ')

function jsonResponse(data, status = 200, headers = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...JSON_HEADERS, ...headers },
  })
}

function methodNotAllowed(allowed) {
  return jsonResponse(
    { detail: '请求方法不受支持。' },
    405,
    { Allow: allowed.join(', ') },
  )
}

function notFound() {
  return jsonResponse({ detail: '未找到请求的内容。' }, 404)
}

function cleanNullableFields(row, fields) {
  if (!row) return row
  for (const field of fields) {
    if (row[field] === null) row[field] = ''
  }
  return row
}

function normalizeMember(row) {
  return cleanNullableFields(row, [
    'major_class',
    'tenure',
    'introduction',
    'welcome_message',
    'photo',
  ])
}

function normalizeActivity(row) {
  cleanNullableFields(row, ['activity_date', 'introduction', 'cover'])
  row.media = []
  return row
}

async function hashClientKey(request) {
  const source =
    request.headers.get('CF-Connecting-IP') ||
    request.headers.get('X-Forwarded-For') ||
    'unknown-client'
  const digest = await crypto.subtle.digest(
    'SHA-256',
    new TextEncoder().encode(source),
  )
  return [...new Uint8Array(digest)]
    .map((value) => value.toString(16).padStart(2, '0'))
    .join('')
}

async function consumeMessageRateLimit(db, request) {
  const clientKey = await hashClientKey(request)
  const now = Math.floor(Date.now() / 1000)
  const expiredBefore = now - 3600
  const row = await db
    .prepare(
      `INSERT INTO message_rate_limits (
         client_key, window_started_at, request_count
       ) VALUES (?1, ?2, 1)
       ON CONFLICT(client_key) DO UPDATE SET
         request_count = CASE
           WHEN window_started_at <= ?3 THEN 1
           ELSE request_count + 1
         END,
         window_started_at = CASE
           WHEN window_started_at <= ?3 THEN ?2
           ELSE window_started_at
         END
       RETURNING request_count`,
    )
    .bind(clientKey, now, expiredBefore)
    .first()
  return row.request_count <= 5
}

async function getProfile(db) {
  const row = await db
    .prepare(
      `SELECT introduction, welcome_slogan, recruitment_info,
              contact_info, qq_group_qr_code, updated_at
       FROM department_profile
       WHERE id = 1`,
    )
    .first()
  return row
    ? cleanNullableFields(row, ['contact_info', 'qq_group_qr_code'])
    : null
}

async function getMembers(db, options = {}) {
  const conditions = ['is_visible = 1']
  const bindings = []
  if (options.current) {
    conditions.push(
      'generation = (SELECT MAX(generation) FROM members WHERE is_visible = 1)',
    )
  }
  if (options.id !== undefined) {
    conditions.push('id = ?')
    bindings.push(options.id)
  }
  const statement = db.prepare(
    `SELECT ${MEMBER_COLUMNS}
     FROM members
     WHERE ${conditions.join(' AND ')}
     ORDER BY sort_order, generation, id`,
  )
  const result = bindings.length
    ? await statement.bind(...bindings).all()
    : await statement.all()
  return result.results.map(normalizeMember)
}

async function getFaqs(db) {
  const result = await db
    .prepare(
      `SELECT id, question, answer
       FROM faqs
       WHERE is_visible = 1
       ORDER BY sort_order, id`,
    )
    .all()
  return result.results
}

async function getMessages(db) {
  const result = await db
    .prepare(
      `SELECT id, nickname, content, submitted_at
       FROM messages
       WHERE review_status = 'approved' AND is_deleted = 0
       ORDER BY submitted_at DESC, id DESC`,
    )
    .all()
  return result.results
}

async function createMessage(db, request) {
  let payload
  try {
    payload = await request.json()
  } catch {
    return jsonResponse({ detail: '请求内容必须是有效的 JSON。' }, 400)
  }
  const nickname = typeof payload?.nickname === 'string' ? payload.nickname.trim() : ''
  const content = typeof payload?.content === 'string' ? payload.content.trim() : ''
  const nicknameHasControl = /[\u0000-\u001f\u007f]/u.test(nickname)
  const contentHasControl = /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/u.test(content)
  if (!nickname || nickname.length > 50 || nicknameHasControl) {
    return jsonResponse(
      { nickname: ['昵称不能为空、不得超过 50 个字符，且不能包含控制字符。'] },
      400,
    )
  }
  if (content.length < 2 || content.length > 1000 || contentHasControl) {
    return jsonResponse(
      { content: ['留言内容须为 2 至 1000 个字符，且不能包含控制字符。'] },
      400,
    )
  }
  if (!(await consumeMessageRateLimit(db, request))) {
    return jsonResponse(
      { detail: '提交过于频繁，请一小时后再试。' },
      429,
      { 'Retry-After': '3600' },
    )
  }
  const result = await db
    .prepare(
      `INSERT INTO messages (
         nickname, content, review_status, reviewed_at
       ) VALUES (
         ?1, ?2, 'approved', strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
       )
       RETURNING id, nickname, content, review_status, submitted_at`,
    )
    .bind(nickname, content)
    .first()
  return jsonResponse(result, 201)
}

async function getActivities(db, activityId) {
  const bindings = []
  let condition = 'is_visible = 1'
  if (activityId !== undefined) {
    condition += ' AND id = ?'
    bindings.push(activityId)
  }
  const statement = db.prepare(
    `SELECT ${ACTIVITY_COLUMNS}
     FROM activities
     WHERE ${condition}
     ORDER BY sort_order, activity_date DESC, id`,
  )
  const result = bindings.length
    ? await statement.bind(...bindings).all()
    : await statement.all()
  const activities = result.results.map(normalizeActivity)
  if (!activities.length) return activities

  const activityById = new Map(activities.map((item) => [item.id, item]))
  const placeholders = activities.map(() => '?').join(', ')
  const mediaResult = await db
    .prepare(
      `SELECT id, activity_id, file, media_type, description, width, height
       FROM activity_media
       WHERE activity_id IN (${placeholders})
       ORDER BY activity_id, sort_order, id`,
    )
    .bind(...activities.map((item) => item.id))
    .all()
  for (const media of mediaResult.results) {
    const activity = activityById.get(media.activity_id)
    delete media.activity_id
    if (activity) activity.media.push(media)
  }
  return activities
}

function parseDetailId(pathname, resource) {
  const match = pathname.match(new RegExp(`^/api/${resource}/(\\d+)/$`))
  if (!match) return undefined
  const id = Number(match[1])
  return Number.isSafeInteger(id) && id > 0 ? id : undefined
}

function authorizeAdmin(request, env) {
  if (!env.ADMIN_API_TOKEN) {
    return jsonResponse(
      { detail: '管理员口令尚未配置，请联系网站管理员。' },
      503,
    )
  }
  const authorization = request.headers.get('Authorization') || ''
  if (authorization !== `Bearer ${env.ADMIN_API_TOKEN}`) {
    return jsonResponse(
      { detail: '管理员口令无效。' },
      401,
      { 'WWW-Authenticate': 'Bearer' },
    )
  }
  return null
}

async function getAdminMessages(db) {
  const result = await db
    .prepare(
      `SELECT id, nickname, content, submitted_at
       FROM messages
       WHERE review_status = 'approved' AND is_deleted = 0
       ORDER BY submitted_at DESC, id DESC`,
    )
    .all()
  return result.results
}

async function deleteAdminMessage(db, messageId) {
  const deleted = await db
    .prepare(
      `UPDATE messages
       SET is_deleted = 1,
           deleted_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
       WHERE id = ?1 AND is_deleted = 0
       RETURNING id`,
    )
    .bind(messageId)
    .first()
  if (!deleted) return null
  await db
    .prepare(
      `INSERT INTO message_review_log (message_id, action, note)
       VALUES (?1, 'deleted', '管理员通过评论管理页删除')`,
    )
    .bind(messageId)
    .run()
  return deleted
}

async function routeRequest(request, env) {
  const db = env.DB
  const url = new URL(request.url)
  const pathname = url.pathname.endsWith('/') ? url.pathname : `${url.pathname}/`
  const method = request.method.toUpperCase()

  if (pathname === '/api/admin/messages/') {
    const authError = authorizeAdmin(request, env)
    if (authError) return authError
    return method === 'GET'
      ? jsonResponse(await getAdminMessages(db))
      : methodNotAllowed(['GET'])
  }
  const adminMessageId = parseDetailId(pathname, 'admin/messages')
  if (adminMessageId !== undefined) {
    const authError = authorizeAdmin(request, env)
    if (authError) return authError
    if (method !== 'DELETE') return methodNotAllowed(['DELETE'])
    const deleted = await deleteAdminMessage(db, adminMessageId)
    return deleted ? new Response(null, { status: 204 }) : notFound()
  }

  if (pathname === '/api/health/') {
    return method === 'GET'
      ? jsonResponse({ status: 'ok', database: 'cloudflare-d1' })
      : methodNotAllowed(['GET'])
  }
  if (pathname === '/api/profile/') {
    if (method !== 'GET') return methodNotAllowed(['GET'])
    const profile = await getProfile(db)
    return profile ? jsonResponse(profile) : notFound()
  }
  if (pathname === '/api/members/' || pathname === '/api/members/current/') {
    if (method !== 'GET') return methodNotAllowed(['GET'])
    return jsonResponse(
      await getMembers(db, { current: pathname.endsWith('/current/') }),
    )
  }
  const memberId = parseDetailId(pathname, 'members')
  if (memberId !== undefined) {
    if (method !== 'GET') return methodNotAllowed(['GET'])
    const members = await getMembers(db, { id: memberId })
    return members.length ? jsonResponse(members[0]) : notFound()
  }
  if (pathname === '/api/activities/') {
    if (method !== 'GET') return methodNotAllowed(['GET'])
    return jsonResponse(await getActivities(db))
  }
  const activityId = parseDetailId(pathname, 'activities')
  if (activityId !== undefined) {
    if (method !== 'GET') return methodNotAllowed(['GET'])
    const activities = await getActivities(db, activityId)
    return activities.length ? jsonResponse(activities[0]) : notFound()
  }
  if (pathname === '/api/faqs/') {
    return method === 'GET'
      ? jsonResponse(await getFaqs(db))
      : methodNotAllowed(['GET'])
  }
  if (pathname === '/api/messages/') {
    if (method === 'GET') return jsonResponse(await getMessages(db))
    if (method === 'POST') return createMessage(db, request)
    return methodNotAllowed(['GET', 'POST'])
  }
  return notFound()
}

export async function onRequest(context) {
  if (!context.env.DB) {
    return jsonResponse(
      { detail: 'Cloudflare D1 数据库尚未绑定，请联系网站管理员。' },
      503,
    )
  }
  try {
    return await routeRequest(context.request, context.env)
  } catch (error) {
    console.error('Cloudflare Pages API error', error)
    return jsonResponse({ detail: '服务器暂时无法处理请求，请稍后重试。' }, 500)
  }
}
