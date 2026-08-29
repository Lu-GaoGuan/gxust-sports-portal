const REQUEST_HEADERS_TO_REMOVE = [
  'connection',
  'host',
  'origin',
  'referer',
  'x-forwarded-host',
  'x-forwarded-proto',
]

const RESPONSE_HEADERS_TO_REMOVE = [
  'access-control-allow-credentials',
  'access-control-allow-headers',
  'access-control-allow-methods',
  'access-control-allow-origin',
]

function errorResponse(message, status) {
  return new Response(JSON.stringify({ detail: message }), {
    status,
    headers: {
      'Cache-Control': 'no-store',
      'Content-Type': 'application/json; charset=utf-8',
    },
  })
}

function getRenderOrigin(value) {
  try {
    const url = new URL(value)
    if (url.protocol !== 'https:' || !url.hostname.endsWith('.onrender.com')) return null
    return url
  } catch {
    return null
  }
}

export async function onRequest({ request, env }) {
  const renderOrigin = getRenderOrigin(env.RENDER_API_ORIGIN)
  if (!renderOrigin) {
    return errorResponse('后端服务尚未配置。', 503)
  }

  const incomingUrl = new URL(request.url)
  const upstreamUrl = new URL(renderOrigin)
  upstreamUrl.pathname = `/api${incomingUrl.pathname.slice('/api'.length)}`
  upstreamUrl.search = incomingUrl.search

  const headers = new Headers(request.headers)
  const clientIp = headers.get('CF-Connecting-IP')
  REQUEST_HEADERS_TO_REMOVE.forEach((header) => headers.delete(header))
  if (clientIp) headers.set('X-Forwarded-For', clientIp)

  const requestInit = {
    method: request.method,
    headers,
    redirect: 'manual',
  }
  if (request.method !== 'GET' && request.method !== 'HEAD') {
    requestInit.body = request.body
  }

  try {
    const upstreamResponse = await fetch(upstreamUrl, requestInit)
    const responseHeaders = new Headers(upstreamResponse.headers)
    RESPONSE_HEADERS_TO_REMOVE.forEach((header) => responseHeaders.delete(header))
    responseHeaders.set('X-Content-Source', 'render-api')

    return new Response(upstreamResponse.body, {
      status: upstreamResponse.status,
      statusText: upstreamResponse.statusText,
      headers: responseHeaders,
    })
  } catch {
    return errorResponse('后端服务暂时无法连接，请稍后重试。', 502)
  }
}
