import { useState } from "react";
import {
  PaymentElement,
  useStripe,
  useElements,
} from "@stripe/react-stripe-js";
import { useTranslation } from "react-i18next";
import { Button } from "#/components/ui/button.tsx";
import SectionCardSkeleton from "../../general/SectionCardSkeleton.tsx";
import NavigationButtonWrapper from "../../general/NavigationButtonWrapper.tsx";
import Spinner from "../../general/Spinner.tsx";
import { useQuery } from "@tanstack/react-query";
import { reservationDetailQueryOptions } from "#/lib/api.ts";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:3000";

interface StripePaymentFormProps {
  reservationId: string;
  onSuccess: () => void;
  onError: () => void;
  onCancel: () => void;
}

export default function StripePaymentForm({
  reservationId,
  onSuccess,
  onError,
  onCancel,
}: StripePaymentFormProps) {
  const { t } = useTranslation();
  const stripe = useStripe();
  const elements = useElements();
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // this same query is hit on the parent PaymentPage, so it will be cached
  const { data: reservation } = useQuery(
    reservationDetailQueryOptions(reservationId),
  );

  const handleSubmit = async (e: React.SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setIsProcessing(true);
    setErrorMessage(null);

    try {
      const { error } = await stripe.confirmPayment({
        elements,
        confirmParams: {
          return_url: `${API_URL}/payments/return/stripe?reservationId=${reservationId}`,
          payment_method_data: {
            billing_details: {
              // hardcode the billing details. cant reliably display the country drop down, so have to pass this info to stripe manually.
              // shouldnt affect payment success
              name: `${reservation?.firstName} ${reservation?.lastName}`,
              email: reservation?.email,
              address: {
                country: "DE",
                postal_code: "00000",
                line1: "N/A",
                line2: null,
                city: "N/A",
                state: null,
              },
            },
          },
        },
        redirect: "if_required",
      });

      if (error) {
        setErrorMessage(error.message ?? "An error occurred");
        setIsProcessing(false);
        if (error.type !== "validation_error") {
          onError();
        }
      } else {
        onSuccess();
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "An error occurred";
      setErrorMessage(message);
      setIsProcessing(false);
      onError();
    }
  };

  if (!stripe || !elements) {
    return <SectionCardSkeleton lines={5} />;
  }

  return (
    <>
      {isProcessing && <Spinner />}
      <form onSubmit={handleSubmit} className="flex flex-col">
        <div className="mb-6 [&_iframe]:outline-none">
          <PaymentElement
            options={{
              layout: "accordion",
              fields: {
                billingDetails: {
                  address: "never",
                },
              },
              wallets: {
                applePay: "auto",
                googlePay: "auto",
              },
            }}
          />
        </div>

        {errorMessage && (
          <div className="mb-4 p-3 bg-white/10 border-2 border-destructive text-red/30 text-xl">
            <p className="text-red-300 text-center">{errorMessage}</p>
          </div>
        )}
        <NavigationButtonWrapper>
          <Button type="submit" disabled={isProcessing}>
            {isProcessing ? t("button_processing") : t("button_pay_now")}
          </Button>
          <Button type="button" variant="secondary" onClick={onCancel}>
            {t("button_back")}
          </Button>
        </NavigationButtonWrapper>
      </form>
    </>
  );
}
