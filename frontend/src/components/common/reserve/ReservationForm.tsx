import FormField from '#/components/common/reserve/FormField.tsx'
import { Field, FieldLabel } from '#/components/ui/field.tsx'
import { Input } from '#/components/ui/input.tsx'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '#/components/ui/select.tsx'
import type { MockShow } from '#/lib/mock-shows.ts'

interface ReservationFormProps {
  show: MockShow
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
  return (
    <div className="w-full flex flex-col md:flex-row justify-center mx-auto gap-16 my-8">
      <div className="p-4">
        <h3 className="text-3xl text-primary">Tickets</h3>
        <Field className="my-1">
          <FieldLabel htmlFor="event" className="min-w-[150px] inline-block text-lg">
            Event
          </FieldLabel>
          <Select value={selectedEventId} onValueChange={setSelectedEventId}>
            <SelectTrigger id="event" className="w-full">
              <SelectValue placeholder="Termin wählen" />
            </SelectTrigger>
            <SelectContent>
              {show.events.map((event) => (
                <SelectItem key={event.id} value={event.id}>
                  {event.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </Field>
        <Field className="my-1">
          <FieldLabel htmlFor="attendee-count" className="min-w-[150px] inline-block text-lg">
            Tickets
          </FieldLabel>
          <Input
            id="attendee-count"
            type="number"
            min={1}
            max={10}
            value={attendeeCount}
            onChange={(e) =>
              setAttendeeCount(
                Math.min(10, Math.max(1, Number(e.target.value) || 1)),
              )
            }
          />
        </Field>
        {!show.baseTicketPrice && (
          <p className="w-full my-4">
            For your Reservation, you will have to pay{' '}
            {show.reservationPrice ?? 5} Euro per Ticket. This will be fully
            deducted from your entree fee at the box office.
          </p>
        )}
      </div>

      <div className="hidden md:block border-r border-primary" />

      <div className="p-4">
        <h3 className="text-3xl text-primary">Personal Information</h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 my-1 justify-center">
          <FormField id="first-name" label="First name" name="first_name" required />
          <FormField id="last-name" label="Last name" name="last_name" required />
        </div>
        <FormField id="email" label="Email" name="email" type="email" required />
      </div>
    </div>
  )
}
