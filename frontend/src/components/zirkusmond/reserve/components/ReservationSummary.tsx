import type { ReservationDetail } from '#/interfaces/reservation.ts'

interface ReservationSummaryProps {
  reservation: ReservationDetail
  customTicketPrice: number
}

export default function ReservationSummary({
  reservation,
  customTicketPrice,
}: ReservationSummaryProps) {
  const total = customTicketPrice * reservation.ticketCount

  return (
    <div className="flex flex-col text-center text-lg gap-2">
      <h3 className="text-center mb-12">Reservation Summary</h3>

      <dl className="space-y-2">
        <div className="flex justify-between gap-4">
          <dt className="opacity-70">Show</dt>
          <dd className="text-right">{reservation.showTitle}</dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="opacity-70">Date</dt>
          <dd className="text-right">{reservation.eventDate}</dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="opacity-70">Booked by</dt>
          <dd className="text-right">
            {reservation.firstName} {reservation.lastName}
          </dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="opacity-70">Tickets</dt>
          <dd className="text-right">{reservation.ticketCount}</dd>
        </div>
      </dl>

      {reservation.guests.length > 0 &&
        reservation.guests.map((guest, index) => (
          <div className="flex justify-between">
            <dt className="opacity-70">Guest {index + 1}</dt>

            <dd key={index}>
              {guest.firstName} {guest.lastName}
            </dd>
          </div>
        ))}

      <div className="flex justify-between">
        <span className="opacity-70">Price per ticket</span>
        <span>{customTicketPrice.toFixed(2)} €</span>
      </div>
      <div className="flex justify-between font-bold mt-2 text-xl">
        <span>Total</span>
        <span>{total.toFixed(2)} €</span>
      </div>
    </div>
  )
}
