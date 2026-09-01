import { Elements } from "@stripe/react-stripe-js";
import { loadStripe } from "@stripe/stripe-js";
import type { Appearance, StripeElementsOptions } from "@stripe/stripe-js";
import StripePaymentForm from "./StripePaymentForm.tsx";

const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE);

// Same Google Fonts stylesheet already loaded for Manrope in styles.css -
// Stripe renders Elements in an iframe so the font has to be handed to it explicitly.
const MANROPE_FONT_SRC =
  "https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap";

// Mirrors the look of the inputs in components/zirkusmond/form/ (see Input in
// components/ui/input.tsx): bg-black/10, border-2 border-primary, rounded-none,
// white text, muted-foreground placeholders, no focus ring/shadow.
const appearance: Appearance = {
  variables: {
    colorPrimary: "#f6ae42",
    colorBackground: "#FFFFFF1A",
    colorText: "#ffffff",
    colorTextPlaceholder: "#dedede",
    colorDanger: "#ef4444",
    fontFamily: "Manrope, sans-serif",
    fontSizeBase: "1.25rem",
    borderRadius: "0px",
  },
  rules: {
    ".Input": {
      border: "2px solid var(--colorPrimary)",
      backgroundColor: "var(--colorBackground)",
      padding: "10px 12px",
      boxShadow: "none",
    },
    ".Block": {
      backgroundColor: "#FFFFFF1A",
      border: "2px solid var(--colorPrimary)",
      borderRadius: "0px",
      boxShadow: "none",
    },
    ".Tab:hover": {
      color: "var(--colorPrimary)",
    },
    ".Tab--selected, .Tab--selected:focus, .Tab--selected:hover": {
      color: "var(--colorPrimary)",
    },
    ".AccordionItem:hover": {
      color: "var(--colorPrimary)",
    },
  },
};

interface StripePaymentWrapperProps {
  clientSecret: string;
  reservationId: string;
  onSuccess: () => void;
  onError: () => void;
  onCancel: () => void;
}

export default function StripePaymentWrapper({
  clientSecret,
  reservationId,
  onSuccess,
  onError,
  onCancel,
}: StripePaymentWrapperProps) {
  const options: StripeElementsOptions = {
    clientSecret,
    appearance,
    fonts: [{ cssSrc: MANROPE_FONT_SRC }],
  };

  return (
    <Elements stripe={stripePromise} options={options}>
      <StripePaymentForm
        reservationId={reservationId}
        onSuccess={onSuccess}
        onError={onError}
        onCancel={onCancel}
      />
    </Elements>
  );
}
