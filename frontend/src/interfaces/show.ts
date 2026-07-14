export interface ShowCard {
  id: number
  title: string
  cardImage: string
  eventDates: string[]
}

export interface HomepageResponse {
  upcomingShows: ShowCard[]
}

export interface ShowDetailEvent {
  id: number
  elaborateDateStr: string
  admissionTime: string
  beginTime: string
  reservationCapacity: number
  reservationOpen: boolean
}

export interface ShowDetail {
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
  upcomingEvents?: ShowDetailEvent[]
  lastModified: string
}

export interface ShowDetailResponse {
  show: ShowDetail
}
