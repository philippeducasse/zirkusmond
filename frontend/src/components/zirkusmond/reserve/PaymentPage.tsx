import { useNavigate } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'

import { reservationDetailQueryOptions } from '#/lib/api.ts'
import PaymentSection from './components/PaymentSection.tsx'
import ReservationSummary from './components/ReservationSummary.tsx'
import SectionCard from '../general/SectionCard.tsx'

interface PaymentPageProps {
  showId: string
  reservationId: string
  customTicketPrice: number
  clientSecret: string
}

export default function PaymentPage({
  showId,
  reservationId,
  customTicketPrice,
  clientSecret,
}: PaymentPageProps) {
  const navigate = useNavigate()
  const reservationQuery = useQuery(
    reservationDetailQueryOptions(reservationId),
  )

  function handlePaymentSuccess() {
    navigate({
      to: '/payment/success',
      search: {
        reservationId,
      },
    })
  }

  function handlePaymentError() {
    navigate({
      to: '/payment/failure',
      search: {
        eventShowId: showId,
      },
    })
  }

  function handlePaymentCancel() {
    navigate({ to: '/reserve/$showId', params: { showId } })
  }

  if (!reservationQuery.data) {
    return null
  }

  return (
    <div className="flex flex-col items-center justify-center gap-8 mx-auto text-white p-1 md:p-8">
      <div className="max-w-xl">
        <SectionCard className="p-12">
          <ReservationSummary
            reservation={reservationQuery.data}
            customTicketPrice={customTicketPrice}
          />
        </SectionCard>
      </div>
      <div className="w-full">
        <SectionCard className="overflow-visible">
          <PaymentSection
            clientSecret={clientSecret}
            reservationId={reservationId}
            onPaymentSuccess={handlePaymentSuccess}
            onPaymentError={handlePaymentError}
            onPaymentCancel={handlePaymentCancel}
          />
        </SectionCard>
      </div>
    </div>
  )
}
