import { createFileRoute } from '@tanstack/react-router'

import EventsSection from '#/components/common/home/EventsSection.tsx'
import FooterSection from '#/components/common/home/FooterSection.tsx'
import GallerySection from '#/components/common/home/GallerySection.tsx'
import Hero from '#/components/common/home/Hero.tsx'

export const Route = createFileRoute('/')({
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
  return (
    <>
      <Hero />
      <EventsSection showAllEventsLink />
      <GallerySection />
      <FooterSection />
    </>
  )
}
