import { useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { Button } from '#/components/ui/button.tsx'
import type { Show } from '#/interfaces/show.ts'
import { useCreateReservation } from '#/lib/payments.ts'
import GuestForm from './components/GuestForm.tsx'
import ReservationForm from './components/ReservationForm.tsx'
import NewsletterForm from './components/NewsletterForm.tsx'
import SlidingScale from './components/SlidingScale.tsx'
import SectionDivider from '../general/SectionDivider.tsx'
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
  const [error, setError] = useState<string | null>(null)

  const guestCount = Math.min(9, Math.max(0, attendeeCount - 1))

  const mutation = useCreateReservation()

  function handleSubmit(e: React.SubmitEvent<HTMLFormElement>) {
    e.preventDefault()
    setError(null)

    const formData = new FormData(e.currentTarget)
    const guests = []

    for (let i = 0; i < guestCount; i++) {
      guests.push({
        firstName: formData.get(`guest-${i}-first-name`) as string,
        lastName: formData.get(`guest-${i}-last-name`) as string,
      })
    }

    mutation.mutate(
      {
        showId: String(show.id),
        eventId: selectedEventId,
        firstName: formData.get('firstName') as string,
        lastName: formData.get('lastName') as string,
        email: formData.get('email') as string,
        newsletter,
        attendeeCount,
        guests,
        customTicketPrice: customPrice,
      },
      {
        onSuccess: (data) => {
          navigate({
            to: '/reserve/$showId/payment',
            params: { showId: String(show.id) },
            search: {
              reservationId: data.reservationId,
              customTicketPrice: customPrice,
            },
          })
        },
        onError: (err) => {
          setError(err instanceof Error ? err.message : 'An error occurred')
        },
      },
    )
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

          <div className="my-4 sm:my-6">
            <SlidingScale
              show={show}
              customPrice={customPrice}
              setCustomPrice={setCustomPrice}
            />
          </div>

          <div className="my-3 sm:my-4 text-center">
            <h4>
              Total Price:{' '}
              <span className="font-bold">
                {(attendeeCount * customPrice).toFixed(2)}
              </span>{' '}
              €
            </h4>
          </div>

          {error && (
            <div className="mb-4 p-3 border bg-white/20 border-red-500 rounded text-xl text-red-200">
              {error}
            </div>
          )}

          <div className=" flex justify-between mt-8 text-center">
            <Button type="button" variant="secondary" onClick={handleBack}>
              Back to Show
            </Button>
            <Button
              type="submit"
              disabled={mutation.isPending}
              className="min-w-[200px]"
            >
              {mutation.isPending ? 'Processing...' : 'Proceed to Payment'}
            </Button>
          </div>
        </SectionCard>
      </form>
    </div>
  )
}
