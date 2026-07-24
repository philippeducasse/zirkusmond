import { useState } from 'react'
import { PaymentElement, useStripe, useElements } from '@stripe/react-stripe-js'
import { Button } from '#/components/ui/button.tsx'

interface StripePaymentFormProps {
  onSuccess: () => void
  onError: (error: string) => void
  onCancel: () => void
}

export default function StripePaymentForm({
  onSuccess,
  onError,
  onCancel,
}: StripePaymentFormProps) {
  const stripe = useStripe()
  const elements = useElements()
  const [isProcessing, setIsProcessing] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  async function handleSubmit(e: React.SubmitEvent<HTMLFormElement>) {
    e.preventDefault()

    if (!stripe || !elements) {
      return
    }

    setIsProcessing(true)
    setErrorMessage(null)

    try {
      const { error } = await stripe.confirmPayment({
        elements,
        confirmParams: {
          return_url: `${window.location.origin}/payment/success`,
        },
        redirect: 'if_required',
      })

      if (error) {
        setErrorMessage(error.message ?? 'An error occurred')
        onError(error.message ?? 'An error occurred')
      } else {
        onSuccess()
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'An error occurred'
      setErrorMessage(message)
      onError(message)
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col">
      <div className="mb-6 [&_iframe]:outline-none">
        <PaymentElement
          options={{
            layout: 'tabs',
          }}
        />
      </div>

      {errorMessage && (
        <div className="mb-4 p-3 bg-white/10 border-2 border-destructive text-red/30 text-xl">
          {errorMessage}
        </div>
      )}

      <div className="mt-8 flex items-center justify-between">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Back
        </Button>
        <Button type="submit" disabled={!stripe || isProcessing}>
          {isProcessing ? 'Processing...' : 'Pay Now'}
        </Button>
      </div>
    </form>
  )
}
