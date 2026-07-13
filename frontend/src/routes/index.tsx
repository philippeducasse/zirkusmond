import { createFileRoute } from '@tanstack/react-router'
import { useSuspenseQuery } from '@tanstack/react-query'

import EventsSection from '#/components/common/home/EventsSection.tsx'
import FooterSection from '#/components/common/home/FooterSection.tsx'
import GallerySection from '#/components/common/home/GallerySection.tsx'
import Hero from '#/components/common/home/Hero.tsx'
import { homepageQueryOptions } from '#/lib/api.ts'

export const Route = createFileRoute('/')({
  loader: ({ context: { queryClient } }) =>
    queryClient.ensureQueryData(homepageQueryOptions),
  head: () => ({
    meta: [
      { title: 'Zirkus Mond' },
      {
        name: 'description',
        content:
          'Zirkus Mond – Dein Zirkus in Berlin! Entdecke unser Programm: Live Shows, Events, Community und zeitgenössische Zirkuskunst im Herzen Berlins.',
      },
      {
        name: 'keywords',
        content:
          'Zirkus Mond Berlin, Zirkus Mond Shows, Zirkus Mond Events, Zirkus Mond Tickets, Live Shows Berlin, Kulturveranstaltungen Berlin, zeitgenössischer Zirkus Berlin, unabhängiger Zirkus Berlin',
      },
    ],
  }),
  component: App,
})

function App() {
  const { data } = useSuspenseQuery(homepageQueryOptions)

  return (
    <>
      <Hero />
      <EventsSection shows={data.upcoming_shows} showAllEventsLink />
      <GallerySection />
      <FooterSection />
    </>
  )
}
