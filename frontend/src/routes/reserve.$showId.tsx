import { createFileRoute, notFound } from '@tanstack/react-router'

import PageContainer from '#/components/common/PageContainer.tsx'
import ReservationForm from '#/components/common/reserve/ReservationForm.tsx'
import { getMockShowById } from '#/lib/mock-shows.ts'

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
      <ReservationForm show={show} />
    </PageContainer>
  )
}
