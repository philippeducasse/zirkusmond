import { Elements } from '@stripe/react-stripe-js'
import { loadStripe } from '@stripe/stripe-js'
import StripePaymentForm from './StripePaymentForm.tsx'

const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY)

interface StripePaymentWrapperProps {
  clientSecret: string
  onSuccess: () => void
  onError: (error: string) => void
}

export default function StripePaymentWrapper({
  clientSecret,
  onSuccess,
  onError,
}: StripePaymentWrapperProps) {
  const options = {
    clientSecret,
    appearance: {
      variables: {
        colorPrimary: '#d4af37',
        colorBackground: '#1a1a2e',
        colorText: '#f0e6d2',
        colorDanger: '#ff6b6b',
        fontFamily: 'Raleway Variable, sans-serif',
      },
    },
  }

  return (
    <Elements stripe={stripePromise} options={options}>
      <StripePaymentForm onSuccess={onSuccess} onError={onError} />
    </Elements>
  )
}
