import { createFileRoute } from '@tanstack/react-router'
import { useSuspenseQuery } from '@tanstack/react-query'

import EventsSection from '#/components/zirkusmond/home/EventsSection'
import GallerySection from '#/components/zirkusmond/home/GallerySection'
import Hero from '#/components/zirkusmond/home/Hero'
import { homepageQueryOptions } from '#/lib/api.ts'
import PageContainer from '#/components/zirkusmond/general/PageContainer'
import ContactSection from '#/components/zirkusmond/home/ContactSection'

export const Route = createFileRoute('/')({
  // TanStack Query: `ensureQueryData` fetches into the cache unless the data
  // is already there. On the server this runs during SSR and the result is
  // dehydrated into the HTML; useSuspenseQuery below then reads it from cache.
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
  // TanStack Query: resolves instantly from the cache filled by the loader
  // (no loading state needed); would suspend only on a cache miss.
  const { data } = useSuspenseQuery(homepageQueryOptions)

  return (
    <>
      <Hero />
      <PageContainer className="pt-0">
        <EventsSection shows={data.upcomingShows} showAllEventsLink />
        {/* <GallerySection /> */}
        <ContactSection />
      </PageContainer>
    </>
  )
}
