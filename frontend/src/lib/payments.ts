import { postJson } from '#/lib/api.ts'
import { useMutation } from '@tanstack/react-query'

interface CreateReservationRequest {
  eventId: string
  firstName: string
  lastName: string
  email: string
  newsletter: boolean
  attendeeCount: number
  customPrice?: number
  guests: Array<{ firstName: string; lastName: string }>
}

interface CreateReservationResponse {
  reservationId: string
}

export async function createReservation(
  showId: string,
  data: CreateReservationRequest,
): Promise<CreateReservationResponse> {
  return postJson(`/reservation/${showId}`, {
    event_id: data.eventId,
    first_name: data.firstName,
    last_name: data.lastName,
    email: data.email,
    newsletter: data.newsletter,
    attendee_count: data.attendeeCount,
    custom_price: data.customPrice,
    guests: data.guests.map((g) => ({
      first_name: g.firstName,
      last_name: g.lastName,
    })),
  })
}

interface CreatePaymentIntentRequest {
  customTicketPrice: number
  paymentMethod: 'card' | 'paypal'
}

interface CreatePaymentIntentResponse {
  id: string
  clientSecret: string
}

export async function createPaymentIntent(
  reservationId: string,
  data: CreatePaymentIntentRequest,
): Promise<CreatePaymentIntentResponse> {
  return postJson(`/payments/${reservationId}/intent`, {
    custom_ticket_price: data.customTicketPrice,
    payment_method: data.paymentMethod,
  })
}

interface CreateReservationWithPaymentParams {
  showId: string
  eventId: string
  firstName: string
  lastName: string
  email: string
  newsletter: boolean
  attendeeCount: number
  guests: Array<{ firstName: string; lastName: string }>
  customTicketPrice: number
}

export function useCreateReservationWithPayment() {
  return useMutation({
    mutationFn: async (params: CreateReservationWithPaymentParams) => {
      const reservation = await createReservation(params.showId, {
        eventId: params.eventId,
        firstName: params.firstName,
        lastName: params.lastName,
        email: params.email,
        newsletter: params.newsletter,
        attendeeCount: params.attendeeCount,
        customPrice: params.customTicketPrice,
        guests: params.guests,
      })

      const paymentIntent = await createPaymentIntent(reservation.reservationId, {
        customTicketPrice: params.customTicketPrice,
        paymentMethod: 'card',
      })

      return paymentIntent
    },
  })
}