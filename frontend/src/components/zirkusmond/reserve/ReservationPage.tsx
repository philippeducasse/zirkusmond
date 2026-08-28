import { useEffect, useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { Button } from '#/components/ui/button.tsx'
import type { Show } from '#/interfaces/show.ts'
import { useCreateReservation, createPaymentIntent } from '#/lib/payments.ts'
import { fillReservationFormWithDummyData } from './fillDummyData.ts'
import GuestForm from './components/GuestForm.tsx'
import ReservationForm from './components/ReservationForm.tsx'
import NewsletterForm from './components/NewsletterForm.tsx'
import SlidingScale from './components/SlidingScale.tsx'
import SectionCard from '../general/SectionCard.tsx'
import NavigationButtonWrapper from '../general/NavigationButtonWrapper.tsx'
import { useTranslation } from 'react-i18next'
import { clearFieldError, validateReservationForm } from './validateForm.ts'

interface ReservationPageProps {
  show: Show
}

export default function ReservationPage({ show }: ReservationPageProps) {
  const { t } = useTranslation()
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
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [isProcessing, setIsProcessing] = useState(false)

  const guestCount = Math.min(9, Math.max(0, attendeeCount - 1))

  const mutation = useCreateReservation()

  function handleClearFieldError(id: string) {
    setFieldErrors((prev) => clearFieldError(prev, id))
  }

  function handleSubmit(e: React.SubmitEvent<HTMLFormElement>) {
    e.preventDefault()
    setError(null)
    setIsProcessing(true)

    const formData = new FormData(e.currentTarget)
    const guests: { firstName: string; lastName: string }[] = []

    for (let i = 0; i < guestCount; i++) {
      guests.push({
        firstName: formData.get(`guest-${i}-first-name`) as string,
        lastName: formData.get(`guest-${i}-last-name`) as string,
      })
    }
    const guestFormData = {
      firstName: formData.get('firstName') as string,
      lastName: formData.get('lastName') as string,
      email: formData.get('email') as string,
      guests,
    }

    const errors = validateReservationForm(guestFormData, guestCount, t)
    setFieldErrors(errors)

    const firstErrorId = Object.keys(errors)[0]
    if (firstErrorId) {
      setIsProcessing(false)
      document.getElementById(firstErrorId)?.focus()
      return
    }

    mutation.mutate(
      {
        ...guestFormData,
        showId: String(show.id),
        eventId: selectedEventId,
        newsletter,
        attendeeCount,
        customTicketPrice: customPrice,
      },
      {
        onSuccess: async (data) => {
          try {
            const paymentIntent = await createPaymentIntent(
              data.reservationId,
              customPrice,
            )
            navigate({
              to: '/reserve/$showId/payment',
              params: { showId: String(show.id) },
              search: {
                reservationId: data.reservationId,
                customTicketPrice: customPrice,
                clientSecret: paymentIntent.clientSecret,
              },
            })
          } catch (err) {
            setIsProcessing(false)
            setError(
              err instanceof Error
                ? err.message
                : t('reservation_error_generic'),
            )
          }
        },
        onError: (err) => {
          setIsProcessing(false)
          setError(
            err instanceof Error ? err.message : t('reservation_error_generic'),
          )
        },
      },
    )
  }

  function handleBack() {
    navigate({ to: '/show/$showId', params: { showId: String(show.id) } })
  }

  function handleFillDummyData() {
    fillReservationFormWithDummyData({
      show,
      setSelectedEventId,
      setAttendeeCount,
      setNewsletter,
      setCustomPrice,
    })
  }

  return (
    <div className="flex items-center justify-center max-w-7xl mx-auto text-white p-1 md:p-8">
      <form onSubmit={handleSubmit} id="reservation-form" noValidate>
        {import.meta.env.DEV && (
          <div className="flex justify-end mb-2">
            <Button
              type="button"
              variant="secondary"
              onClick={handleFillDummyData}
            >
              {t('button_fill_test_data')}
            </Button>
          </div>
        )}
        <SectionCard>
          <ReservationForm
            show={show}
            selectedEventId={selectedEventId}
            setSelectedEventId={setSelectedEventId}
            attendeeCount={attendeeCount}
            setAttendeeCount={setAttendeeCount}
            fieldErrors={fieldErrors}
            clearFieldError={handleClearFieldError}
          />

          <GuestForm
            guestCount={guestCount}
            fieldErrors={fieldErrors}
            clearFieldError={handleClearFieldError}
          />
          <NewsletterForm
            newsletter={newsletter}
            setNewsletter={setNewsletter}
          />

          <div className="my-4 sm:my-6 max-w-2xl mx-auto">
            <SlidingScale
              show={show}
              customPrice={customPrice}
              setCustomPrice={setCustomPrice}
            />
          </div>

          <div className="my-3 sm:my-4 text-center">
            <h4>
              {t('reservation_total_price')}:{' '}
              <span className="font-bold">
                {(attendeeCount * customPrice).toFixed(2)}
              </span>{' '}
              €
            </h4>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-white/10 border-2 border-destructive text-red/30 text-xl">
              <p className="text-red-300 text-center">{error}</p>
            </div>
          )}

          <NavigationButtonWrapper>
            <Button
              type="submit"
              disabled={isProcessing}
              className="sm:min-w-[200px]"
            >
              {isProcessing
                ? t('button_processing')
                : t('button_proceed_to_payment')}
            </Button>
            <Button type="button" variant="secondary" onClick={handleBack}>
              {t('button_back_to_show')}
            </Button>
          </NavigationButtonWrapper>
        </SectionCard>
      </form>
    </div>
  )
}
