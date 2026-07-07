import type { FormEvent } from 'react'
import { useState } from 'react'

import { Button } from '#/components/ui/button.tsx'
import { Checkbox } from '#/components/ui/checkbox.tsx'
import { Field, FieldLabel } from '#/components/ui/field.tsx'
import { Input } from '#/components/ui/input.tsx'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '#/components/ui/select.tsx'
import { Slider } from '#/components/ui/slider.tsx'
import type { MockShow } from '#/lib/mock-shows.ts'

interface ReservationFormProps {
  show: MockShow
}

export default function ReservationForm({ show }: ReservationFormProps) {
  const [selectedEventId, setSelectedEventId] = useState(
    show.events[0]?.id ?? '',
  )
  const [attendeeCount, setAttendeeCount] = useState(1)
  const [customPrice, setCustomPrice] = useState(
    show.baseTicketPrice ?? show.reservationPrice ?? 15,
  )
  const [newsletter, setNewsletter] = useState(false)

  const guestCount = Math.min(9, Math.max(0, attendeeCount - 1))
  const pricePerTicket = show.baseTicketPrice
    ? customPrice
    : (show.reservationPrice ?? 5)
  const total = attendeeCount * pricePerTicket
  const minPrice = show.minTicketPrice ?? (show.baseTicketPrice ?? 0) - 10
  const maxPrice = show.maxTicketPrice ?? (show.baseTicketPrice ?? 0) + 10

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    // TODO: wire up to POST /reservation/:showId and the payment redirect once an API client exists
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="mx-auto max-w-4xl text-white"
    >
      <div className="my-8 flex w-full flex-col justify-center gap-16 md:flex-row">
        <div className="flex-1">
          <h3 className="text-3xl text-primary">Tickets</h3>
          <Field className="mt-4">
            <FieldLabel htmlFor="event">Event</FieldLabel>
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
          <Field className="mt-4">
            <FieldLabel htmlFor="attendee-count">Tickets</FieldLabel>
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
            <p className="my-4 w-full">
              For your Reservation, you will have to pay{' '}
              {show.reservationPrice ?? 5} Euro per Ticket. This will be
              fully deducted from your entree fee at the box office.
            </p>
          )}
        </div>

        <div className="hidden border-r border-primary md:block" />

        <div className="flex-1">
          <h3 className="text-3xl text-primary">Personal Information</h3>
          <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
            <Field>
              <FieldLabel htmlFor="first-name">First name</FieldLabel>
              <Input id="first-name" name="first_name" required />
            </Field>
            <Field>
              <FieldLabel htmlFor="last-name">Last name</FieldLabel>
              <Input id="last-name" name="last_name" required />
            </Field>
          </div>
          <Field className="mt-4">
            <FieldLabel htmlFor="email">Email</FieldLabel>
            <Input id="email" name="email" type="email" required />
          </Field>
        </div>
      </div>

      {guestCount > 0 && (
        <div className="my-8 flex flex-col gap-6">
          {Array.from({ length: guestCount }, (_, i) => (
            <div key={i} className="border border-primary/40 p-4">
              <h4 className="mb-4 text-lg text-primary">Guest {i + 1}</h4>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <Field>
                  <FieldLabel htmlFor={`guest-${i}-first-name`}>
                    First name
                  </FieldLabel>
                  <Input id={`guest-${i}-first-name`} name={`guest-${i}-first-name`} required />
                </Field>
                <Field>
                  <FieldLabel htmlFor={`guest-${i}-last-name`}>
                    Last name
                  </FieldLabel>
                  <Input id={`guest-${i}-last-name`} name={`guest-${i}-last-name`} required />
                </Field>
              </div>
            </div>
          ))}
        </div>
      )}

      <Field orientation="horizontal" className="my-6">
        <Checkbox
          id="newsletter"
          checked={newsletter}
          onCheckedChange={(checked) => setNewsletter(checked === true)}
        />
        <FieldLabel htmlFor="newsletter" className="font-normal">
          I would like to receive the Zirkus Mond newsletter.
        </FieldLabel>
      </Field>

      <div className="my-6">
        <h3 className="text-4xl text-primary">Payment</h3>
        {show.baseTicketPrice && (
          <div className="my-6">
            <h4 className="mb-3 text-2xl text-primary">Choose Your Price</h4>
            <p className="my-6 text-lg">
              We offer sliding scale pricing to make our shows accessible.
              Pay what feels right for you! Your generosity directly
              supports the artists and sustains our community.
            </p>
            <div className="mb-4 flex items-center justify-center gap-3">
              <span className="text-xl font-bold text-primary">
                Price per Ticket:
              </span>
              <span className="text-xl font-bold text-primary">
                {customPrice} EUR
              </span>
            </div>
            <Slider
              value={[customPrice]}
              onValueChange={([value]) => setCustomPrice(value)}
              min={minPrice}
              max={maxPrice}
              step={1}
            />
            <div className="mt-2 flex justify-between text-sm">
              <span>Soli price: {minPrice} EUR</span>
              <span>Standard: {show.baseTicketPrice} EUR</span>
              <span>Support price: {maxPrice} EUR</span>
            </div>
          </div>
        )}
      </div>

      <div className="my-4 text-center">
        <h4 className="mb-3 text-2xl text-primary">
          Total Price: <span className="font-bold">{total.toFixed(2)}</span> €
        </h4>
      </div>

      <h4 className="my-12 text-center text-2xl text-primary">
        Choose Your Payment Method
      </h4>
      <div className="flex flex-col justify-evenly gap-4 md:flex-row">
        <Button type="submit" name="payment-method" value="paypal">
          PayPal
        </Button>
        <Button type="submit" name="payment-method" value="stripe">
          Bank Card
        </Button>
      </div>
    </form>
  )
}
