import { useEffect } from 'react'

export interface GuestFormData {
  firstName: string
  lastName: string
  email: string
  guests: { firstName: string; lastName: string }[]
}

export interface ReservationDraft extends GuestFormData {
  selectedEventId: string
  attendeeCount: number
  customPrice: number
  newsletter: boolean
}

export function extractGuestFormData(
  formData: FormData,
  guestCount: number,
): GuestFormData {
  const guests: GuestFormData['guests'] = []

  for (let i = 0; i < guestCount; i++) {
    guests.push({
      firstName: formData.get(`guest-${i}-first-name`) as string,
      lastName: formData.get(`guest-${i}-last-name`) as string,
    })
  }

  return {
    firstName: formData.get('firstName') as string,
    lastName: formData.get('lastName') as string,
    email: formData.get('email') as string,
    guests,
  }
}

const DRAFT_KEY = 'reservation-draft'

export function loadDraft(): ReservationDraft | null {
  const draftJson = sessionStorage.getItem(DRAFT_KEY)
  if (!draftJson) return null

  try {
    return JSON.parse(draftJson)
  } catch (error) {
    console.error(`Failed to parse field inputs: ${draftJson}, error: ${error}`)
    return null
  }
}

export function saveDraft(draft: ReservationDraft) {
  sessionStorage.setItem(DRAFT_KEY, JSON.stringify(draft))
}

export function clearDraft() {
  sessionStorage.removeItem(DRAFT_KEY)
}

export function setFormValue(name: string, value: string | undefined) {
  if (value === undefined || value === null) return

  const form = document.getElementById(
    'reservation-form',
  ) as HTMLFormElement | null
  if (!form) return

  const el = form.elements.namedItem(name)
  if (el instanceof HTMLInputElement) el.value = value
}

export function useFormStorage(savedInputs: ReservationDraft | null) {
  useEffect(() => {
    if (!savedInputs) return

    setFormValue('firstName', savedInputs.firstName)
    setFormValue('lastName', savedInputs.lastName)
    setFormValue('email', savedInputs.email)

    savedInputs.guests.forEach((guest, i) => {
      setFormValue(`guest-${i}-first-name`, guest.firstName)
      setFormValue(`guest-${i}-last-name`, guest.lastName)
    })
  })
}
