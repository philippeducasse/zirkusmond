import StripePaymentWrapper from './StripePaymentWrapper.tsx'

interface PaymentSectionProps {
  clientSecret: string
  onPaymentSuccess: () => void
  onPaymentError: (error: string) => void
}

export default function PaymentSection({
  clientSecret,
  onPaymentSuccess,
  onPaymentError,
}: PaymentSectionProps) {
  return (
    <>
      <div className="my-4 sm:my-6">
        <h3 className="text-center">Payment</h3>
      </div>

      <div className="my-6">
        <StripePaymentWrapper
          clientSecret={clientSecret}
          onSuccess={onPaymentSuccess}
          onError={onPaymentError}
        />
      </div>
    </>
  )
}
