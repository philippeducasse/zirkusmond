import type { Show } from '#/interfaces/show.ts'
import SlidingScale from './SlidingScale.tsx'
import StripePaymentWrapper from './StripePaymentWrapper.tsx'

interface PaymentSectionProps {
  show: Show
  attendeeCount: number
  customPrice: number
  setCustomPrice: (price: number) => void
  clientSecret: string | null
  onPaymentSuccess: () => void
  onPaymentError: (error: string) => void
}

export default function PaymentSection({
  show,
  attendeeCount,
  customPrice,
  setCustomPrice,
  clientSecret,
  onPaymentSuccess,
  onPaymentError,
}: PaymentSectionProps) {
  const pricePerTicket = show.baseTicketPrice
    ? customPrice
    : (show.reservationPrice ?? 5)
  const total = attendeeCount * pricePerTicket

  return (
    <>
      <div className="my-4 sm:my-6">
        <h3 className="text-center">Payment</h3>
        <SlidingScale
          show={show}
          customPrice={customPrice}
          setCustomPrice={setCustomPrice}
        />
      </div>

      <div className="my-3 sm:my-4 text-center">
        <h4>
          Total Price: <span className="font-bold">{total.toFixed(2)}</span> €
        </h4>
      </div>

      <div className="my-6">
        {clientSecret ? (
          <StripePaymentWrapper
            clientSecret={clientSecret}
            onSuccess={onPaymentSuccess}
            onError={onPaymentError}
          />
        ) : (
          <div className="text-center text-gray-400">
            Loading payment form...
          </div>
        )}
      </div>
    </>
  )
}
