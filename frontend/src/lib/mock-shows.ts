export interface MockShowEvent {
  id: string
  /** Full display date, e.g. "Sonntag 05.07.26 um 20:00" (used on cards and the reservation event picker). */
  label: string
  beginTime: string
  admissionTime: string
}

export interface MockShow {
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
  /** Fixed reservation deposit per ticket; rest is paid at the door. Mutually exclusive with baseTicketPrice. */
  reservationPrice: number | null
  /** Default price on the sliding scale. When set, the reservation form shows a price slider instead of a fixed reservation price. */
  baseTicketPrice: number | null
  minTicketPrice: number | null
  maxTicketPrice: number | null
  events: MockShowEvent[]
}

export const MOCK_SHOWS: MockShow[] = [
  {
    id: 'open-stage-vol-3',
    title: 'Open Stage - 2026 - Vol. III',
    cardImage: '/images/team/maria.webp',
    bannerImage: '/images/general/zm_banner.webp',
    description:
      'Eine bunte Nacht offener Bühne: Artistik, Comedy, Musik und Überraschungen von und mit unserer Community. Jede Ausgabe ist einzigartig – komm vorbei und lass dich verzaubern.',
    cast: 'Wechselnde Artist:innen aus der Berliner Zirkus- und Performance-Szene.',
    videoLink: 'https://www.youtube.com/channel/UCa4CK1Fl7ZpTA6mz04wH6CA',
    websiteLink: undefined,
    reservationPrice: 5,
    baseTicketPrice: null,
    minTicketPrice: null,
    maxTicketPrice: null,
    events: [
      {
        id: 'e1',
        label: 'Sonntag 05.07.26 um 20:00',
        beginTime: '20:00',
        admissionTime: '19:30',
      },
      {
        id: 'e2',
        label: 'Sonntag 12.07.26 um 20:00',
        beginTime: '20:00',
        admissionTime: '19:30',
      },
      {
        id: 'e3',
        label: 'Sonntag 19.07.26 um 20:00',
        beginTime: '20:00',
        admissionTime: '19:30',
      },
      {
        id: 'e4',
        label: 'Sonntag 26.07.26 um 20:00',
        beginTime: '20:00',
        admissionTime: '19:30',
      },
    ],
  },
  {
    id: 'nachtfalter',
    title: 'Nachtfalter',
    cardImage: '/images/team/valerio.webp',
    bannerImage: '/images/general/zirkus-mond-zelt.webp',
    description:
      'Ein immersiver Abend zwischen Traum und Wirklichkeit: Luftakrobatik, Tanz und Live-Musik verweben sich zu einer nächtlichen Reise unter der Zirkuskuppel.',
    cast: 'Ensemble Nachtfalter, mit Gastauftritten internationaler Artist:innen.',
    websiteLink: 'https://zirkusmond.de',
    reservationPrice: null,
    baseTicketPrice: 20,
    minTicketPrice: 10,
    maxTicketPrice: 30,
    events: [
      {
        id: 'e5',
        label: 'Freitag 14.08.26 um 19:30',
        beginTime: '19:30',
        admissionTime: '19:00',
      },
      {
        id: 'e6',
        label: 'Samstag 15.08.26 um 19:30',
        beginTime: '19:30',
        admissionTime: '19:00',
      },
      {
        id: 'e7',
        label: 'Sonntag 16.08.26 um 18:00',
        beginTime: '18:00',
        admissionTime: '17:30',
      },
    ],
  },
  {
    id: 'mondlicht-gala',
    title: 'Mondlicht Gala',
    cardImage: '/images/team/MnM.webp',
    bannerImage: '/images/general/zm_banner.webp',
    description:
      'Unsere jährliche Gala-Show mit den besten Nummern der Saison – festlich, funkelnd und voller Überraschungen.',
    cast: 'Das gesamte Zirkus Mond Ensemble.',
    reservationPrice: null,
    baseTicketPrice: null,
    minTicketPrice: null,
    maxTicketPrice: null,
    thirdPartyReservation: true,
    thirdPartyReservationLink: 'https://www.eventbrite.com',
    events: [
      {
        id: 'e8',
        label: 'Freitag 04.09.26 um 20:00',
        beginTime: '20:00',
        admissionTime: '19:30',
      },
    ],
  },
  {
    id: 'zirkuszelt-spezial',
    title: 'Zirkuszelt Spezial',
    cardImage: '/images/logos/mond.webp',
    bannerImage: '/images/general/zirkus-mond-zelt.webp',
    description:
      'Ein besonderer Abend für die ganze Familie mit klassischen Zirkusnummern in neuem Gewand.',
    cast: 'Familie Mond und Freunde.',
    reservationPrice: 5,
    baseTicketPrice: null,
    minTicketPrice: null,
    maxTicketPrice: null,
    events: [
      {
        id: 'e9',
        label: 'Samstag 19.09.26 um 20:00',
        beginTime: '20:00',
        admissionTime: '19:30',
      },
      {
        id: 'e10',
        label: 'Sonntag 20.09.26 um 18:00',
        beginTime: '18:00',
        admissionTime: '17:30',
      },
    ],
  },
]

export function getMockShowById(id: string): MockShow | undefined {
  return MOCK_SHOWS.find((show) => show.id === id)
}
