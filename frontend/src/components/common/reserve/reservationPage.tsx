import type { FormEvent } from 'react'
import { useState } from 'react'
import { useNavigate } from '@tanstack/react-router'

import type { MockShow } from '#/lib/mock-shows.ts'

import GuestForm from './GuestForm.tsx'
import PaymentSection from './PaymentSection.tsx'
import ReservationForm from './ReservationForm.tsx'

interface ReservationPageProps {
  show: MockShow
}

export default function ReservationPage({ show }: ReservationPageProps) {
  const navigate = useNavigate()
  const [selectedEventId, setSelectedEventId] = useState(
    show.events[0]?.id ?? '',
  )
  const [attendeeCount, setAttendeeCount] = useState(1)
  const [customPrice, setCustomPrice] = useState(
    show.baseTicketPrice ?? show.reservationPrice ?? 15,
  )
  const [newsletter, setNewsletter] = useState(false)

  const guestCount = Math.min(9, Math.max(0, attendeeCount - 1))

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    // TODO: wire up to POST /reservation/:showId and the payment redirect once an API client exists
  }

  function handleBack() {
    navigate({ to: '/show/$showId', params: { showId: show.id } })
  }

  return (
    <div className="flex items-center justify-center max-w-7xl mx-auto text-white p-8">
      <form onSubmit={handleSubmit} id="reservation-form">
        <ReservationForm
          show={show}
          selectedEventId={selectedEventId}
          setSelectedEventId={setSelectedEventId}
          attendeeCount={attendeeCount}
          setAttendeeCount={setAttendeeCount}
        />

        <GuestForm guestCount={guestCount} />

        <PaymentSection
          show={show}
          attendeeCount={attendeeCount}
          customPrice={customPrice}
          setCustomPrice={setCustomPrice}
          newsletter={newsletter}
          setNewsletter={setNewsletter}
          onBack={handleBack}
        />
      </form>
    </div>
  )
}