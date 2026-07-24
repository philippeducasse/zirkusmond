import { createFileRoute, redirect } from '@tanstack/react-router'

import PageContainer from '#/components/zirkusmond/general/PageContainer'
import PageHeader from '#/components/zirkusmond/general/PageHeader'
import PaymentPage from '#/components/zirkusmond/reserve/PaymentPage'

interface PaymentSearch {
  reservationId: string
  customTicketPrice: number
}

function validatePaymentSearch(search: Record<string, unknown>): PaymentSearch {
  return {
    reservationId: typeof search.reservationId === 'string' ? search.reservationId : '',
    customTicketPrice: Number(search.customTicketPrice),
  }
}

export const Route = createFileRoute('/reserve/$showId_/payment')({
  validateSearch: validatePaymentSearch,
  // validateSearch stays lenient/coercive; this is the single place that
  // decides whether the params are actually usable and redirects back to the
  // reservation form if someone lands here directly without a
  // reservationId/price from step one (bookmark, back button, manual URL).
  beforeLoad: ({ search, params }) => {
    if (!search.reservationId || !Number.isFinite(search.customTicketPrice)) {
      throw redirect({ to: '/reserve/$showId', params: { showId: params.showId } })
    }
  },
  component: RouteComponent,
})

function RouteComponent() {
  const { showId } = Route.useParams()
  const { reservationId, customTicketPrice } = Route.useSearch()

  return (
    <PageContainer>
      <PageHeader>Payment</PageHeader>
      <PaymentPage
        showId={showId}
        reservationId={reservationId}
        customTicketPrice={customTicketPrice}
      />
    </PageContainer>
  )
}