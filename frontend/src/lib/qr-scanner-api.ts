import { queryOptions } from '@tanstack/react-query'

import type {
  CheckInResponse,
  QRScannerEvent,
} from '#/interfaces/qr-scanner.ts'
import { apiUrl } from '#/lib/api.ts'
import { keysToCamelCase } from '#/lib/utils.ts'

async function fetchJsonWithAuth<T>(path: string): Promise<T> {
  const res = await fetch(apiUrl(path), {
    credentials: 'include',
  })
  if (!res.ok) {
    throw new Error(`API request to ${path} failed with status ${res.status}`)
  }
  const data = await res.json()
  return keysToCamelCase<T>(data)
}

export const qrScannerEventsQueryOptions = queryOptions({
  queryKey: ['qr-scanner-events'],
  queryFn: () => fetchJsonWithAuth<QRScannerEvent[]>('/qr-scanner/get-events'),
})

export async function checkInTicket(
  ticketUuid: string,
): Promise<CheckInResponse> {
  const res = await fetch(apiUrl(`/qr-scanner/${ticketUuid}/check-in`), {
    method: 'POST',
    credentials: 'include',
  })
  if (!res.ok) {
    throw new Error(`Check-in request failed with status ${res.status}`)
  }
  const data = await res.json()
  return keysToCamelCase<CheckInResponse>(data)
}
