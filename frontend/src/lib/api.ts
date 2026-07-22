import { queryOptions } from '@tanstack/react-query'

import type { HomepageResponse, ShowDetailResponse } from '#/interfaces/show.ts'
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

export class ApiError extends Error {
  constructor(
    public status: number,
    path: string,
  ) {
    super(`API request to ${path} failed with status ${status}`)
  }
}

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(apiUrl(path))
  if (!res.ok) {
    throw new ApiError(res.status, path)
  }
  const data = await res.json()
  return keysToCamelCase<T>(data)
}

export async function postJson<T>(
  path: string,
  body: unknown,
  options?: { skipCamelCase?: boolean },
): Promise<T> {
  const res = await fetch(apiUrl(path), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    throw new ApiError(res.status, path)
  }
  const data = await res.json()
  return options?.skipCamelCase ? data : keysToCamelCase<T>(data)
}

/**
 * TanStack Query: `queryOptions` bundles a cache key with its fetch function
 * so the same definition can be used by route loaders (ensureQueryData) and
 * components (useSuspenseQuery). Sharing one definition guarantees both sides
 * hit the same cache entry.
 */
export const homepageQueryOptions = queryOptions({
  // Cache key: all consumers of ['homepage'] share one cached response.
  queryKey: ['homepage'],
  queryFn: () => fetchJson<HomepageResponse>('/'),
})

/**
 * TanStack Query: parameterised query — a factory because the cache key must
 * include the showId, giving each show its own cache entry.
 */
export const showQueryOptions = (showId: string) =>
  queryOptions({
    queryKey: ['show', showId],
    queryFn: async () => {
      const data = await fetchJson<ShowDetailResponse>(`/shows/${showId}`)
      return data.show
    },
  })

export const reserveQueryOptions = () =>
  queryOptions({
    queryKey: ['reserve'],
  })
