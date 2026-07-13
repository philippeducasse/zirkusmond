export interface ShowCard {
  id: number
  title: string
  card_image: string
  event_dates: string[]
}

export interface HomepageResponse {
  upcoming_shows: ShowCard[]
}