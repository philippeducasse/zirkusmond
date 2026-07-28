import type { CheckInSuccess as CheckInSuccessData } from '#/interfaces/qr-scanner.ts'

interface CheckInSuccessProps {
  data: CheckInSuccessData
}

export function CheckInSuccess({ data }: CheckInSuccessProps) {
  return (
    <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
      <h2 className="font-bold text-green-800 text-6xl mb-2">Checked In</h2>
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
              <p className="text-6xl">
                <strong>Tickets:</strong> {data.guests.length}
              </p>
              <p className="text-5xl">
                <strong>Guests:</strong> {data.guests.join(', ')}
              </p>
            </>
          ) : (
            <p className="text-5xl">
              <strong>Guest:</strong> {data.guests[0]}
            </p>
          )}
          <p className="text-5xl">
            <strong>Reservation ID:</strong> {data.reservationNumber}
          </p>
        </div>
      </div>
    </div>
  )
}