import { createFileRoute } from '@tanstack/react-router'

import { SERVER_API_URL } from '#/lib/api.ts'

async function proxyToDjango({
  request,
  params,
}: {
  request: Request
  params: { _splat?: string }
}) {
  const url = new URL(request.url)
  const target = `${SERVER_API_URL}/${params._splat ?? ''}${url.search}`

  const headers = new Headers(request.headers)
  headers.delete('host')

  const hasBody = request.method !== 'GET' && request.method !== 'HEAD'

  const res = await fetch(target, {
    method: request.method,
    headers,
    body: hasBody ? request.body : undefined,
    // Node's fetch requires `duplex` when streaming a request body.
    duplex: hasBody ? 'half' : undefined,
  } as RequestInit & { duplex?: 'half' })

  const resHeaders = new Headers(res.headers)
  // Node's fetch already decompressed the body; these headers would lie.
  resHeaders.delete('content-encoding')
  resHeaders.delete('content-length')

  return new Response(res.body, { status: res.status, headers: resHeaders })
}

export const Route = createFileRoute('/api/$')({
  server: {
    handlers: {
      GET: proxyToDjango,
      POST: proxyToDjango,
      PUT: proxyToDjango,
      PATCH: proxyToDjango,
      DELETE: proxyToDjango,
    },
  },
})