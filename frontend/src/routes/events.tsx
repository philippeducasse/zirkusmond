import { createFileRoute } from '@tanstack/react-router'
import { useSuspenseQuery } from '@tanstack/react-query'

import EventsSection from '#/components/common/home/EventsSection.tsx'
import PageContainer from '#/components/common/PageContainer.tsx'
import { homepageQueryOptions } from '#/lib/api.ts'

export const Route = createFileRoute('/events')({
  loader: ({ context: { queryClient } }) =>
    queryClient.ensureQueryData(homepageQueryOptions),
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
  const { data } = useSuspenseQuery(homepageQueryOptions)

  return (
    <PageContainer>
      <EventsSection shows={data.upcomingShows} showHomeLink />
    </PageContainer>
  )
}
