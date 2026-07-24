import { Elements } from '@stripe/react-stripe-js'
import {
  loadStripe,
  type Appearance,
  type StripeElementsOptions,
} from '@stripe/stripe-js'
import StripePaymentForm from './StripePaymentForm.tsx'

const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY)

// Same Google Fonts stylesheet already loaded for Manrope in styles.css -
// Stripe renders Elements in an iframe so the font has to be handed to it explicitly.
const MANROPE_FONT_SRC =
  'https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap'

// Mirrors the look of the inputs in components/zirkusmond/form/ (see Input in
// components/ui/input.tsx): bg-black/10, border-2 border-primary, rounded-none,
// white text, muted-foreground placeholders, no focus ring/shadow.
const appearance: Appearance = {
  theme: 'flat',
  variables: {
    colorPrimary: '#f6ae42',
    colorBackground: '#FFFFFF1A',
    colorText: '#ffffff',
    colorTextPlaceholder: '#dedede',
    colorDanger: '#ef4444',
    fontFamily: 'Manrope, sans-serif',
    fontSizeBase: '16px',
    borderRadius: '0px',
  },
  rules: {
    '.Input': {
      border: '2px solid var(--colorPrimary)',
      backgroundColor: 'var(--colorBackground)',
      padding: '10px 12px',
      boxShadow: 'none',
    },
    '.Input:focus': {
      border: '2px solid var(--colorPrimary)',
      boxShadow: 'none',
      outline: 'none',
    },
    '.Input--invalid': {
      border: '2px solid var(--colorDanger)',
      boxShadow: 'none',
    },
    '.Label': {
      color: '#ffffff',
      fontFamily: 'Manrope, sans-serif',
      fontSize: '16px',
      fontWeight: '500',
      marginBottom: '6px',
    },
    '.Tab': {
      border: '2px solid var(--colorPrimary)',
      backgroundColor: '#FFFFFF1A',
      borderRadius: '0px',
      boxShadow: 'none',
    },
    '.Tab:hover': {
      backgroundColor: 'rgba(0, 0, 0, 0.2)',
      boxShadow: 'none',
    },
    '.Tab--selected': {
      border: '2px solid var(--colorPrimary)',
      backgroundColor: 'rgba(246, 174, 66, 0.15)',
      boxShadow: 'none',
    },
    '.Tab--selected:hover': {
      backgroundColor: 'rgba(246, 174, 66, 0.15)',
    },
    '.TabLabel': {
      color: '#ffffff',
    },
    '.TabLabel--selected': {
      color: '#f6ae42',
    },
    '.TabIcon': {
      fill: '#ffffff',
    },
    '.TabIcon--selected': {
      fill: '#f6ae42',
    },
    '.Block': {
      backgroundColor: '#FFFFFF1A',
      border: '2px solid var(--colorPrimary)',
      borderRadius: '0px',
      boxShadow: 'none',
    },
    '.CheckboxInput': {
      backgroundColor: '#FFFFFF1A',
      border: '2px solid var(--colorPrimary)',
      borderRadius: '0px',
    },
    '.CheckboxInput--checked': {
      backgroundColor: '#f6ae42',
      border: '2px solid var(--colorPrimary)',
    },
    '.Error': {
      color: '#EFFFFF4444',
      fontSize: '13px',
    },
  },
}

interface StripePaymentWrapperProps {
  clientSecret: string
  onSuccess: () => void
  onError: (error: string) => void
  onCancel: () => void
}

export default function StripePaymentWrapper({
  clientSecret,
  onSuccess,
  onError,
  onCancel,
}: StripePaymentWrapperProps) {
  const options: StripeElementsOptions = {
    clientSecret,
    appearance,
    fonts: [{ cssSrc: MANROPE_FONT_SRC }],
  }

  return (
    <Elements stripe={stripePromise} options={options}>
      <StripePaymentForm
        onSuccess={onSuccess}
        onError={onError}
        onCancel={onCancel}
      />
    </Elements>
  )
}
