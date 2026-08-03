import { createFileRoute } from '@tanstack/react-router'

import { SERVER_API_URL } from '#/lib/api.ts'

export const Route = createFileRoute('/media/$')({
  server: {
    handlers: {
      GET: async ({ params }) => {
        const res = await fetch(
          `${SERVER_API_URL}/media/${params._splat ?? ''}`,
        )

        const headers = new Headers(res.headers)
        // Node's fetch already decompressed the body; these headers would lie.
        headers.delete('content-encoding')
        headers.delete('content-length')

        return new Response(res.body, { status: res.status, headers })
      },
    },
  },
})