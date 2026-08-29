import { postJson } from "#/lib/api.ts";
import { useMutation } from "@tanstack/react-query";

interface CreateReservationRequest {
  eventId: string;
  firstName: string;
  lastName: string;
  email: string;
  newsletter: boolean;
  attendeeCount: number;
  customPrice?: number;
  guests: Array<{ firstName: string; lastName: string }>;
}

interface CreateReservationResponse {
  reservationId: string;
}

export const createReservation = async (
  showId: string,
  data: CreateReservationRequest,
): Promise<CreateReservationResponse> => {
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
  });
};

interface CreatePaymentIntentResponse {
  id: string;
  clientSecret: string;
}

export const createPaymentIntent = async (
  reservationId: string,
  customTicketPrice: number,
): Promise<CreatePaymentIntentResponse> => {
  return postJson(`/payments/${reservationId}/intent`, {
    customTicketPrice,
  });
};

interface CreateReservationParams {
  showId: string;
  eventId: string;
  firstName: string;
  lastName: string;
  email: string;
  newsletter: boolean;
  attendeeCount: number;
  guests: Array<{ firstName: string; lastName: string }>;
  customTicketPrice: number;
}

export const useCreateReservation = () => {
  return useMutation({
    mutationFn: (params: CreateReservationParams) =>
      createReservation(params.showId, {
        eventId: params.eventId,
        firstName: params.firstName,
        lastName: params.lastName,
        email: params.email,
        newsletter: params.newsletter,
        attendeeCount: params.attendeeCount,
        customPrice: params.customTicketPrice,
        guests: params.guests,
      }),
  });
};

export const useCreatePaymentIntent = (
  reservationId: string,
  customTicketPrice: number,
) => {
  const mutation = useMutation({
    mutationFn: () => createPaymentIntent(reservationId, customTicketPrice),
  });
  console.log({ mutation });
  return mutation.data?.clientSecret;
};
