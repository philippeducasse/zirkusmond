import DynamicForm from '#/components/zirkusmond/form/DynamicForm'
import {
  buildPersonalInfoFields,
  buildTicketFields,
} from '#/components/zirkusmond/reserve/buildFormFields'
import type { Show } from '#/interfaces/show'

interface ReservationFormProps {
  show: Show
  selectedEventId: string
  setSelectedEventId: (id: string) => void
  attendeeCount: number
  setAttendeeCount: (count: number) => void
}

export default function ReservationForm({
  show,
  selectedEventId,
  setSelectedEventId,
  attendeeCount,
  setAttendeeCount,
}: ReservationFormProps) {
  const ticketFields = buildTicketFields({
    show,
    selectedEventId,
    setSelectedEventId,
    attendeeCount,
    setAttendeeCount,
  })
  const personalInfoFields = buildPersonalInfoFields()

  return (
    <div className="w-full flex flex-col justify-center mx-auto gap-4 my-8">
      <div className="p-4 md:p-8">
        <DynamicForm title="Tickets" fields={ticketFields} />

        {!show.baseTicketPrice && (
          <p className="w-full my-3 sm:my-4">
            For your Reservation, you will have to pay{' '}
            {show.reservationPrice ?? 5} Euro per Ticket. This will be fully
            deducted from your entree fee at the box office.
          </p>
        )}
      </div>

      <div className="p-4 md:p-8">
        <DynamicForm title="Personal Information" fields={personalInfoFields} />
      </div>
    </div>
  )
}
