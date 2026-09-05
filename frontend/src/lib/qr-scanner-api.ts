import { queryOptions } from "@tanstack/react-query";

import type {
  CheckInResponse,
  QRScannerEvent,
} from "#/interfaces/qr-scanner.ts";
import { apiUrl } from "#/lib/api.ts";
import { keysToCamelCase } from "#/lib/utils.ts";

const fetchJsonWithAuth = async <T>(path: string): Promise<T> => {
  const res = await fetch(apiUrl(path), {
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error(`API request to ${path} failed with status ${res.status}`);
  }
  const data = await res.json();
  return keysToCamelCase<T>(data);
};

export const qrScannerEventsQueryOptions = queryOptions({
  queryKey: ["qr-scanner-events"],
  queryFn: () => fetchJsonWithAuth<QRScannerEvent[]>("/qr-scanner/get-events"),
});

export const checkInTicket = async (
  ticketUuid: string,
  eventId: number,
): Promise<CheckInResponse> => {
  const res = await fetch(
    apiUrl(`/qr-scanner/${ticketUuid}/check-in?event=${eventId}`),
    {
      method: "POST",
      credentials: "include",
      // Add a timeout to this request so that if something hangs dont have to refresh the entire thing
      signal: AbortSignal.timeout(8000),
    },
  );
  const data = await res.json();
  return keysToCamelCase<CheckInResponse>(data);
};
