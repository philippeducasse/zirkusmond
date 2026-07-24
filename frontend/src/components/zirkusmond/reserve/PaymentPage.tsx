import { useEffect, useRef, useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'

import { reservationDetailQueryOptions } from '#/lib/api.ts'
import { useCreatePaymentIntent } from '#/lib/payments.ts'
import PaymentSection from './components/PaymentSection.tsx'
import ReservationSummary from './components/ReservationSummary.tsx'
import SectionCard from '../general/SectionCard.tsx'

interface PaymentPageProps {
  showId: string
  reservationId: string
  customTicketPrice: number
}

export default function PaymentPage({
  showId,
  reservationId,
  customTicketPrice,
}: PaymentPageProps) {
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)
  const mutation = useCreatePaymentIntent()
  const reservationQuery = useQuery(
    reservationDetailQueryOptions(reservationId),
  )
  const firedRef = useRef(false)

  useEffect(() => {
    if (firedRef.current) return
    firedRef.current = true
    mutation.mutate(
      { reservationId, customTicketPrice },
      {
        onError: (err) => {
          setError(err instanceof Error ? err.message : 'An error occurred')
        },
      },
    )
    // eslint-disable-next-line react-hooks/exhaustive-deps -- fire exactly once per page visit
  }, [])

  function handlePaymentSuccess() {
    // TODO: Create proper success route
    window.location.href = '/payment/success'
  }

  function handlePaymentCancel() {
    navigate({ to: '/reserve/$showId', params: { showId } })
  }

  return (
    <>
      <div className="flex flex-col items-center justify-center gap-8 mx-auto text-white p-1 md:p-8">
        {reservationQuery.data && (
          <div className="max-w-xl">
            <SectionCard className="p-12">
              <ReservationSummary
                reservation={reservationQuery.data}
                customTicketPrice={customTicketPrice}
              />
            </SectionCard>
          </div>
        )}
        <div className="w-full">
          <SectionCard>
            {error && (
              <div className="mb-4 p-3 bg-red-900/20 border border-red-500 rounded text-red-200 text-sm">
                {error}
              </div>
            )}
            {mutation.data && (
              <PaymentSection
                clientSecret={mutation.data.clientSecret}
                onPaymentSuccess={handlePaymentSuccess}
                onPaymentError={setError}
                onPaymentCancel={handlePaymentCancel}
              />
            )}
          </SectionCard>
        </div>
      </div>
    </>
  )
}
