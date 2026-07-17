import { createFileRoute } from '@tanstack/react-router'
import { useSuspenseQuery } from '@tanstack/react-query'

import EventsSection from '#/components/zirkusmond/home/EventsSection'
import PageContainer from '#/components/zirkusmond/general/PageContainer'
import { homepageQueryOptions } from '#/lib/api.ts'

export const Route = createFileRoute('/events')({
  // TanStack Query: prefetch into the cache during SSR / navigation. Reuses
  // the homepage query, so navigating from / renders without a refetch.
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
  // TanStack Query: reads the cache entry the loader ensured; no loading state.
  const { data } = useSuspenseQuery(homepageQueryOptions)

  return (
    <PageContainer>
      <EventsSection shows={data.upcomingShows} showHomeLink />
    </PageContainer>
  )
}
