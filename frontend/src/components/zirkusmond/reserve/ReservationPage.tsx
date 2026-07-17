import type { FormEvent } from 'react'
import { useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { Button } from '#/components/ui/button.tsx'
import type { Show } from '#/interfaces/show.ts'
import GuestForm from './components/GuestForm.tsx'
import PaymentSection from './components/PaymentSection.tsx'
import ReservationForm from './components/ReservationForm.tsx'
import NewsletterForm from './components/NewsletterForm.tsx'
import SectionDivider from '../home/SectionDivider.tsx'
import SectionCard from '../general/SectionCard.tsx'

interface ReservationPageProps {
  show: Show
}

export default function ReservationPage({ show }: ReservationPageProps) {
  const navigate = useNavigate()
  const [selectedEventId, setSelectedEventId] = useState(
    show.upcomingEvents[0]?.id ?? '',
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
    navigate({ to: '/show/$showId', params: { showId: String(show.id) } })
  }

  return (
    <div className="flex items-center justify-center max-w-7xl mx-auto text-white p-1 md:p-8">
      <form onSubmit={handleSubmit} id="reservation-form">
        <SectionCard>
          <ReservationForm
            show={show}
            selectedEventId={selectedEventId}
            setSelectedEventId={setSelectedEventId}
            attendeeCount={attendeeCount}
            setAttendeeCount={setAttendeeCount}
          />

          <GuestForm guestCount={guestCount} />
          <NewsletterForm
            newsletter={newsletter}
            setNewsletter={setNewsletter}
          />
        </SectionCard>

        <SectionDivider type="flower" />
        <SectionCard>
          <PaymentSection
            show={show}
            attendeeCount={attendeeCount}
            customPrice={customPrice}
            setCustomPrice={setCustomPrice}
          />
        </SectionCard>
        <SectionDivider type="moon" />
        <div className="mt-8 text-center">
          <Button
            type="button"
            size={'sm'}
            variant="secondary"
            onClick={handleBack}
          >
            Back to Show
          </Button>
        </div>
      </form>
    </div>
  )
}
