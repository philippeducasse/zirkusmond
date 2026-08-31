import type { CheckInSuccess as CheckInSuccessData } from "#/interfaces/qr-scanner.ts";
import { useTranslation } from "react-i18next";

interface CheckInSuccessProps {
  data: CheckInSuccessData;
}

export const CheckInSuccess = ({ data }: CheckInSuccessProps) => {
  const { t } = useTranslation();
  return (
    <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
      <h2 className="font-bold text-green-800 text-6xl mb-2">{t("qr_checked_in")}</h2>
      <div className="flex flex-col items-center">
        <svg
          className="w-28 h-28 mx-auto text-green-500 mb-4"
          fill="none"
          stroke="currentColor"
          strokeWidth="3"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
        </svg>
        <div className="text-left">
          {data.isGroup ? (
            <>
              <p className="text-6xl text-black">
                <strong>{t("qr_tickets")}:</strong> {data.guests.length}
              </p>
              <p className="text-5xl text-black">
                <strong>{t("qr_guests")}:</strong> {data.guests.join(", ")}
              </p>
            </>
          ) : (
            <p className="text-5xl text-black">
              <strong>{t("qr_guest")}:</strong> {data.guests[0]}
            </p>
          )}
          <p className="text-5xl text-black">
            <strong>{t("qr_reservation_id")}:</strong> {data.reservationNumber}
          </p>
        </div>
      </div>
    </div>
  );
};
