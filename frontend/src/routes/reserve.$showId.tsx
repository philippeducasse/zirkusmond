import { createFileRoute, notFound } from '@tanstack/react-router'

import PageContainer from '#/components/common/PageContainer.tsx'
import ReservationPage from '#/components/common/reserve/reservationPage.tsx'
import { getMockShowById } from '#/lib/interfaces/shows'

export const Route = createFileRoute('/reserve/$showId')({
  loader: ({ params }) => {
    const show = getMockShowById(params.showId)
    if (!show) throw notFound()
    return show
  },
  head: ({ loaderData }) => ({
    meta: loaderData
      ? [{ title: `Zirkus Mond Reservation - ${loaderData.title}` }]
      : [],
  }),
  component: RouteComponent,
})

function RouteComponent() {
  const show = Route.useLoaderData()

  return (
    <PageContainer>
      <h1 className="mb-4 text-center text-3xl text-primary lg:text-5xl">
        {show.title}
      </h1>
      <ReservationPage show={show} />
    </PageContainer>
  )
}
