import { createFileRoute, Link, notFound } from '@tanstack/react-router'

import PageContainer from '#/components/common/PageContainer.tsx'
import SectionDivider from '#/components/common/home/SectionDivider.tsx'
import { ShowDetails } from '#/components/common/show/ShowDetails.tsx'
import TimeDetails from '#/components/common/TimeDetails.tsx'
import { Button } from '#/components/ui/button.tsx'
import type { MockShow } from '#/lib/mock-shows.ts'
import { getMockShowById } from '#/lib/mock-shows.ts'

export const Route = createFileRoute('/show/$showId')({
  loader: ({ params }) => {
    const show = getMockShowById(params.showId)
    if (!show) throw notFound()
    return show
  },
  head: ({ loaderData }) => ({
    meta: loaderData ? [{ title: `Zirkus Mond - ${loaderData.title}` }] : [],
  }),
  component: RouteComponent,
})

function ReserveButton({ show }: { show: MockShow }) {
  if (show.thirdPartyReservation && show.thirdPartyReservationLink) {
    return (
      <Button asChild>
        <a href={show.thirdPartyReservationLink} target="_blank" rel="noreferrer">
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
  const show = Route.useLoaderData()

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
        <Button asChild>
          <Link to="/">Home</Link>
        </Button>
        <ReserveButton show={show} />
      </div>

      <SectionDivider type="flower" />
    </PageContainer>
  )
}
