import { queryOptions } from '@tanstack/react-query'

import type { HomepageResponse } from '#/interfaces/show.ts'
import { keysToCamelCase } from '#/lib/utils.ts'

/**
 * On the server (SSR loaders) we talk to Django directly; in the browser
 * requests go through the Vite dev proxy under /api (see vite.config.ts),
 * which also avoids CORS since Django doesn't send CORS headers.
 */
const SERVER_API_URL = process.env.API_URL ?? 'http://localhost:8000'

function apiUrl(path: string) {
  return typeof window === 'undefined'
    ? `${SERVER_API_URL}${path}`
    : `/api${path}`
}

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(apiUrl(path))
  if (!res.ok) {
    throw new Error(`API request to ${path} failed with status ${res.status}`)
  }
  const data = await res.json()
  return keysToCamelCase<T>(data)
}

export const homepageQueryOptions = queryOptions({
  queryKey: ['homepage'],
  queryFn: () => fetchJson<HomepageResponse>('/'),
})
