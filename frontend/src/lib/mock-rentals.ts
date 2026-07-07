export interface MockRentalObject {
  id: string
  name: string
  description: string
  image: string
  link: string
}

export const MOCK_RENTAL_OBJECTS: MockRentalObject[] = [
  {
    id: 'circus-tent',
    name: 'Zirkuszelt',
    description:
      'Unser Zirkuszelt bietet Platz für bis zu 300 Gäste und eignet sich für Shows, Konzerte und private Events.',
    image: '/images/general/zirkus-mond-zelt.webp',
    link: 'https://zirkusmond.de',
  },
  {
    id: 'stage',
    name: 'Manegenbühne',
    description:
      'Eine mobile Rundbühne, perfekt für Zirkus-, Tanz- und Theaterproduktionen jeder Größe.',
    image: '/images/logos/mond_stage.webp',
    link: 'https://zirkusmond.de',
  },
]
