import { createFileRoute, notFound } from '@tanstack/react-router'
import { useSuspenseQuery } from '@tanstack/react-query'

import PageContainer from '#/components/common/PageContainer.tsx'
import ReservationPage from '#/components/common/reserve/ReservationPage'
import { ApiError, showQueryOptions } from '#/lib/api.ts'

export const Route = createFileRoute('/reserve/$showId')({
  // TanStack Query: same query as /show/$showId, so a user coming from the
  // show page gets an instant render from cache; a 404 becomes notFound.
  loader: async ({ context: { queryClient }, params }) => {
    try {
      return await queryClient.ensureQueryData(showQueryOptions(params.showId))
    } catch (error) {
      if (error instanceof ApiError && error.status === 404) throw notFound()
      throw error
    }
  },
  head: ({ loaderData }) => ({
    meta: loaderData
      ? [{ title: `Zirkus Mond Reservation - ${loaderData.title}` }]
      : [],
  }),
  component: RouteComponent,
})

function RouteComponent() {
  const { showId } = Route.useParams()
  // TanStack Query: reads the cache entry the loader ensured; suspends only
  // on a cache miss.
  const { data: show } = useSuspenseQuery(showQueryOptions(showId))

  return (
    <PageContainer>
      <h1 className="mb-4 text-center text-3xl text-primary lg:text-5xl">
        {show.title}
      </h1>
      <ReservationPage show={show} />
    </PageContainer>
  )
}
