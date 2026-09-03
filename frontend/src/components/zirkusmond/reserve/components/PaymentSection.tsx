import { useTranslation } from "react-i18next";
import StripePaymentWrapper from "./StripePaymentWrapper.tsx";

interface PaymentSectionProps {
  clientSecret: string;
  reservationId: string;
  onPaymentSuccess: () => void;
  onPaymentError: () => void;
  onPaymentCancel: () => void;
}

export default function PaymentSection({
  clientSecret,
  reservationId,
  onPaymentSuccess,
  onPaymentError,
  onPaymentCancel,
}: PaymentSectionProps) {
  const { t } = useTranslation();

  return (
    <>
      <div className="mt-4 sm:mt-6">
        <h3 className="text-center">{t("payment_section_title")}</h3>
        <h5 className="text-white">{t("payment_section_subtitle")}</h5>
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
  );
}
