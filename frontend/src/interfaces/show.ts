export interface ShowCard {
  id: number
  title: string
  cardImage: string
  eventDates: string[]
}

export interface HomepageResponse {
  upcomingShows: ShowCard[]
}

export interface ShowEvent {
  id: string
  /** Full display date, e.g. "Sonntag 05.07.26" (used on cards and the reservation event picker). */
  label: string
  beginTime: string
  admissionTime: string
}

export interface Show {
  id: number
  title: string
  description: string
  cast: string
  cardImage: string
  bannerImage?: string
  videoLink?: string
  websiteLink?: string
  baseTicketPrice?: number
  minTicketPrice?: number
  maxTicketPrice?: number
  reservationPrice?: number
  thirdPartyReservation?: boolean
  thirdPartyReservationLink?: string
  upcomingEvents: ShowEvent[]
  lastModified: string
}

export interface ShowDetailResponse {
  show: Show
}
