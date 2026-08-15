import { useState } from 'react'
import { PaymentElement, useStripe, useElements } from '@stripe/react-stripe-js'
import { Button } from '#/components/ui/button.tsx'
import SectionCardSkeleton from '../../general/SectionCardSkeleton.tsx'

interface StripePaymentFormProps {
  reservationId: string
  onSuccess: () => void
  onError: () => void
  onCancel: () => void
}

export default function StripePaymentForm({
  reservationId,
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
          return_url: `${import.meta.env.VITE_API_URL}/payments/return/stripe?reservationId=${reservationId}`,
          payment_method_data: {
            billing_details: {
              // hardcode the billing details. cant reliably display the country drop down, so have to pass this info to stripe manually.
              // shouldnt affect payment success
              address: {
                country: 'DE',
                postal_code: '00000',
                line1: 'N/A',
                line2: null,
                city: 'N/A',
                state: null,
              },
            },
          },
        },
        redirect: 'if_required',
      })

      if (error) {
        setErrorMessage(error.message ?? 'An error occurred')
        setIsProcessing(false)
        onError()
      } else {
        onSuccess()
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'An error occurred'
      setErrorMessage(message)
      setIsProcessing(false)
      onError()
    }
  }

  if (!stripe || !elements) {
    return <SectionCardSkeleton lines={5} />
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col">
      <div className="mb-6 [&_iframe]:outline-none">
        <PaymentElement
          options={{
            layout: 'tabs',
            fields: {
              billingDetails: {
                address: 'never',
              },
            },
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
        <Button type="submit" disabled={isProcessing}>
          {isProcessing ? 'Processing...' : 'Pay Now'}
        </Button>
      </div>
    </form>
  )
}
