export interface ReservationGuest {
  firstName: string
  lastName: string
}

export interface ReservationDetail {
  showTitle: string
  eventDate: string
  firstName: string
  lastName: string
  ticketCount: number
  guests: ReservationGuest[]
}