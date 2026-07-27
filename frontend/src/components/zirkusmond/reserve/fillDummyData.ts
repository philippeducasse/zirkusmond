import { flushSync } from 'react-dom'
import type { Show } from '#/interfaces/show'

interface FillDummyDataParams {
  show: Show
  setSelectedEventId: (id: string) => void
  setAttendeeCount: (count: number) => void
  setNewsletter: (checked: boolean) => void
  setCustomPrice: (price: number) => void
}

export function fillReservationFormWithDummyData({
  show,
  setSelectedEventId,
  setAttendeeCount,
  setNewsletter,
  setCustomPrice,
}: FillDummyDataParams) {
  const dummyAttendeeCount = 2
  const firstEventId = show.upcomingEvents[0]?.id

  // flushSync forces the guest fields to exist in the DOM before we fill them below.
  flushSync(() => {
    if (firstEventId) setSelectedEventId(firstEventId)
    setAttendeeCount(dummyAttendeeCount)
    setNewsletter(true)
    if (show.baseTicketPrice) setCustomPrice(show.baseTicketPrice)
  })

  const form = document.getElementById(
    'reservation-form',
  ) as HTMLFormElement | null
  if (!form) return

  const setValue = (name: string, value: string) => {
    const el = form.elements.namedItem(name)
    if (el instanceof HTMLInputElement) el.value = value
  }

  setValue('firstName', 'Max')
  setValue('lastName', 'Mustermann')
  setValue('email', `test+${Date.now()}@example.com`)

  const dummyGuestCount = Math.min(9, Math.max(0, dummyAttendeeCount - 1))
  for (let i = 0; i < dummyGuestCount; i++) {
    setValue(`guest-${i}-first-name`, 'Erika')
    setValue(`guest-${i}-last-name`, 'Musterfrau')
  }
}