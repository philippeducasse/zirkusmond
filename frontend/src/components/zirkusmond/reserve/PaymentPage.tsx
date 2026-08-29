import { useNavigate } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";

import { reservationDetailQueryOptions } from "#/lib/api.ts";
import PaymentSection from "./components/PaymentSection.tsx";
import ReservationSummary from "./components/ReservationSummary.tsx";
import SectionCard from "../general/SectionCard.tsx";
import SectionCardSkeleton from "../general/SectionCardSkeleton.tsx";
import ContentSection from "../general/ContentSection.tsx";
import CrossFade from "../general/CrossFade.tsx";

interface PaymentPageProps {
  showId: string;
  reservationId: string;
  customTicketPrice: number;
  clientSecret: string;
}

export default function PaymentPage({
  showId,
  reservationId,
  customTicketPrice,
  clientSecret,
}: PaymentPageProps) {
  const navigate = useNavigate();
  const reservationQuery = useQuery(
    reservationDetailQueryOptions(reservationId),
  );

  const handlePaymentSuccess = () => {
    navigate({
      to: "/payment/success",
      search: {
        reservationId,
      },
    });
  };

  const handlePaymentError = () => {
    navigate({
      to: "/payment/failure",
      search: {
        eventShowId: Number(showId),
      },
    });
  };

  const handlePaymentCancel = () => {
    navigate({ to: "/reserve/$showId", params: { showId } });
  };

  return (
    <ContentSection className="flex flex-col items-center justify-center gap-8">
      <div className="max-w-xl">
        <CrossFade
          isLoading={reservationQuery.isPending}
          skeleton={<SectionCardSkeleton lines={6} className="p-6 sm:p-12" />}
        >
          {reservationQuery.isError ? (
            <SectionCard className="p-6 sm:p-12">
              <p>Error loading reservation details. Please try again.</p>
            </SectionCard>
          ) : reservationQuery.data ? (
            <SectionCard className="p-6 sm:p-12">
              <ReservationSummary
                reservation={reservationQuery.data}
                customTicketPrice={customTicketPrice}
              />
            </SectionCard>
          ) : null}
        </CrossFade>
      </div>
      <div className="w-full">
        <SectionCard className="overflow-visible">
          <PaymentSection
            clientSecret={clientSecret}
            reservationId={reservationId}
            onPaymentSuccess={handlePaymentSuccess}
            onPaymentError={handlePaymentError}
            onPaymentCancel={handlePaymentCancel}
          />
        </SectionCard>
      </div>
    </ContentSection>
  );
}
