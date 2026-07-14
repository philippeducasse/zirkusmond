import { createFileRoute, Link, notFound } from '@tanstack/react-router'
import { useSuspenseQuery } from '@tanstack/react-query'

import PageContainer from '#/components/common/PageContainer.tsx'
import SectionDivider from '#/components/common/home/SectionDivider.tsx'
import { ShowDetails } from '#/components/common/show/ShowDetails.tsx'
import TimeDetails from '#/components/common/TimeDetails.tsx'
import { Button } from '#/components/ui/button.tsx'
import type { Show } from '#/lib/interfaces/shows'
import { ApiError, showQueryOptions } from '#/lib/api.ts'

export const Route = createFileRoute('/show/$showId')({
  // TanStack Query: prefetch the show into the cache during SSR / navigation.
  // The data is also returned so `head` can use it as loaderData; a 404 from
  // the API is translated into the router's notFound page.
  loader: async ({ context: { queryClient }, params }) => {
    try {
      return await queryClient.ensureQueryData(showQueryOptions(params.showId))
    } catch (error) {
      if (error instanceof ApiError && error.status === 404) throw notFound()
      throw error
    }
  },
  head: ({ loaderData }) => ({
    meta: loaderData ? [{ title: `Zirkus Mond - ${loaderData.title}` }] : [],
  }),
  component: RouteComponent,
})

function ReserveButton({ show }: { show: Show }) {
  if (show.thirdPartyReservation && show.thirdPartyReservationLink) {
    return (
      <Button asChild>
        <a
          href={show.thirdPartyReservationLink}
          target="_blank"
          rel="noreferrer"
        >
          Zur Reservierung
        </a>
      </Button>
    )
  }
  return (
    <Button asChild>
      <Link to="/reserve/$showId" params={{ showId: show.id }}>
        {show.baseTicketPrice ? 'Tickets Kaufen' : 'Zur Reservierung'}
      </Link>
    </Button>
  )
}

function RouteComponent() {
  const { showId } = Route.useParams()
  // TanStack Query: same key as the loader, so this reads from the cache the
  // loader filled instead of fetching again.
  const { data: show } = useSuspenseQuery(showQueryOptions(showId))

  return (
    <PageContainer>
      <img
        src={show.bannerImage}
        alt={`${show.title} Banner`}
        className="mx-auto w-full object-cover"
      />

      <div className="flex flex-wrap justify-center gap-6 py-8">
        {show.events.map((event) => (
          <TimeDetails
            key={event.id}
            date={event.label}
            beginTime={event.beginTime}
            admissionTime={event.admissionTime}
          />
        ))}
      </div>

      <div className="my-8 flex justify-center">
        <ReserveButton show={show} />
      </div>

      <SectionDivider type="kite" />

      <ShowDetails show={show} />

      <div className="my-12 flex justify-evenly">
        <Button variant={'secondary'}>
          <Link to="/">Home</Link>
        </Button>
        <ReserveButton show={show} />
      </div>

      <SectionDivider type="flower" />
    </PageContainer>
  )
}
