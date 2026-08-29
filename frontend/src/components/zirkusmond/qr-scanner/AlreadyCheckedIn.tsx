import type { CheckInAlreadyCheckedIn } from "#/interfaces/qr-scanner.ts";

interface AlreadyCheckedInProps {
  data: CheckInAlreadyCheckedIn;
}

export const AlreadyCheckedIn = ({ data }: AlreadyCheckedInProps) => {
  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
      <h2 className="font-bold text-yellow-800 text-6xl mb-2">
        Already Checked In
      </h2>
      <div className="flex flex-col items-center">
        <svg
          className="w-28 h-28 mx-auto text-yellow-500 mb-4"
          fill="none"
          stroke="currentColor"
          strokeWidth="3"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
        <div className="text-left">
          <p className="text-5xl">
            <strong>Reservation ID:</strong> {data.reservationNumber}
          </p>
          <p className="text-5xl">
            <strong>Guests:</strong> {data.guests.join(", ")}
          </p>
        </div>
      </div>
    </div>
  );
};
