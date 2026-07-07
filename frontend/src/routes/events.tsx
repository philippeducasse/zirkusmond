import { createFileRoute } from '@tanstack/react-router'

import EventsSection from '#/components/common/home/EventsSection.tsx'
import PageContainer from '#/components/common/PageContainer.tsx'

export const Route = createFileRoute('/events')({
  head: () => ({
    meta: [
      { title: 'Zirkus Mond – Shows & Events' },
      {
        name: 'description',
        content:
          'Alle Shows und Events im Zirkus Mond Berlin – Trapez, Akrobatik, Cabaret, Varieté, Physical Theatre und mehr. Jetzt Tickets sichern!',
      },
      {
        name: 'keywords',
        content:
          'Zirkus Shows Berlin, Zirkus Events Berlin, Live Shows Berlin, Trapez, Akrobatik Berlin, Cabaret, Varieté, Physical Theatre, Familien Events Berlin',
      },
    ],
  }),
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <PageContainer>
      <EventsSection showHomeLink />
    </PageContainer>
  )
}
