import { createFileRoute } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'

import { QRScannerComponent } from '#/components/zirkusmond/qr-scanner/QRScannerComponent.tsx'
import { qrScannerEventsQueryOptions } from '#/lib/qr-scanner-api.ts'

export const Route = createFileRoute('/qr-scanner')({
  head: () => ({
    meta: [
      { title: 'Zirkus Mond – QR Code Scanner' },
      {
        name: 'description',
        content: 'QR Code Scanner for event check-in at Zirkus Mond Berlin',
      },
    ],
  }),
  component: RouteComponent,
})

function RouteComponent() {
  const { data: events } = useQuery(qrScannerEventsQueryOptions)

  if (!events) return null

  return <QRScannerComponent events={events} />
}
