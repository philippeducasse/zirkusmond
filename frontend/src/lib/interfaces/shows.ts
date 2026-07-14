export interface ShowEvent {
  id: string
  /** Full display date, e.g. "Sonntag 05.07.26" (used on cards and the reservation event picker). */
  label: string
  beginTime: string
  admissionTime: string
}

export interface Show {
  id: string
  title: string
  cardImage: string
  bannerImage: string
  description: string
  cast: string
  videoLink?: string
  websiteLink?: string
  thirdPartyReservation?: boolean
  thirdPartyReservationLink?: string
  reservationPrice: number | null
  baseTicketPrice: number | null
  minTicketPrice: number | null
  maxTicketPrice: number | null
  events: ShowEvent[]
}
