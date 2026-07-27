import StripePaymentWrapper from './StripePaymentWrapper.tsx'

interface PaymentSectionProps {
  clientSecret: string
  reservationId: string
  onPaymentSuccess: () => void
  onPaymentError: () => void
  onPaymentCancel: () => void
}

export default function PaymentSection({
  clientSecret,
  reservationId,
  onPaymentSuccess,
  onPaymentError,
  onPaymentCancel,
}: PaymentSectionProps) {
  return (
    <>
      <div className="my-4 sm:my-6">
        <h3 className="text-center">Payment</h3>
      </div>

      <div className="my-6">
        <StripePaymentWrapper
          clientSecret={clientSecret}
          reservationId={reservationId}
          onSuccess={onPaymentSuccess}
          onError={onPaymentError}
          onCancel={onPaymentCancel}
        />
      </div>
    </>
  )
}
