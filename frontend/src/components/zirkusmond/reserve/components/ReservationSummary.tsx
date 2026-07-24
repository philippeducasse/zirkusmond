import type { ReservationDetail } from '#/interfaces/reservation.ts'
import SectionDivider from '../../general/SectionDivider.tsx'

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
    <div className="text-center text-lg">
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

      {reservation.guests.length > 0 && (
        <ul className="mt-3 space-y-1 opacity-70">
          {reservation.guests.map((guest, index) => (
            <li key={index}>
              {guest.firstName} {guest.lastName}
            </li>
          ))}
        </ul>
      )}

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
