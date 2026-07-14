export interface ShowCard {
  id: number
  title: string
  cardImage: string
  eventDates: string[]
}

export interface HomepageResponse {
  upcomingShows: ShowCard[]
}