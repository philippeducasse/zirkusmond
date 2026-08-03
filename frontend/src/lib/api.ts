import { queryOptions } from '@tanstack/react-query'

import type { ReservationDetail } from '#/interfaces/reservation.ts'
import type { HomepageResponse, ShowDetailResponse } from '#/interfaces/show.ts'
import { keysToCamelCase, keysToSnakeCase } from '#/lib/utils.ts'

/**
 * On the server (SSR loaders) we talk to Django directly; in the browser
 * requests go through the /api/$ server route (see routes/api.$.tsx), which
 * proxies to Django and also avoids CORS since Django doesn't send CORS
 * headers.
 */
export const SERVER_API_URL = process.env.API_URL ?? 'http://localhost:8000'

export function apiUrl(path: string) {
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

export async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(apiUrl(path))
  if (!res.ok) {
    throw new ApiError(res.status, path)
  }
  const data = await res.json()
  return keysToCamelCase<T>(data)
}

export async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(apiUrl(path), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(keysToSnakeCase(body)),
  })
  if (!res.ok) {
    throw new ApiError(res.status, path)
  }
  const data = await res.json()
  return keysToCamelCase<T>(data)
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

export const reservationDetailQueryOptions = (reservationId: string) =>
  queryOptions({
    queryKey: ['reservation', reservationId],
    queryFn: () =>
      fetchJson<ReservationDetail>(`/reservation/detail/${reservationId}`),
  })
