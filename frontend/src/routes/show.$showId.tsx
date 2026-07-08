import { createFileRoute, Link, notFound } from '@tanstack/react-router'

import PageContainer from '#/components/common/PageContainer.tsx'
import SectionDivider from '#/components/common/home/SectionDivider.tsx'
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

      <div className="flex flex-col text-lg lg:text-2xl">
        <div>
          <p className="mt-8 mb-4 text-3xl text-primary">About the show:</p>
          <p>{show.description}</p>
        </div>
        <div className="mt-8 flex flex-wrap justify-center gap-12">
          <img
            src={show.cardImage}
            alt={show.title}
            className="aspect-square w-full max-w-sm object-cover"
          />
          <div className="flex flex-col lg:mt-12">
            <p className="mt-4 mb-4 text-3xl text-primary">Cast:</p>
            <p>{show.cast}</p>
          </div>
        </div>
        <div className="mt-8 flex flex-wrap items-center justify-evenly gap-4">
          {show.videoLink && (
            <a
              className="text-center text-2xl underline hover:text-white"
              href={show.videoLink}
              target="_blank"
              rel="noreferrer"
            >
              Trailer
            </a>
          )}
          {show.websiteLink && (
            <a
              className="text-center text-2xl underline hover:text-white"
              href={show.websiteLink}
              target="_blank"
              rel="noreferrer"
            >
              Company's website
            </a>
          )}
        </div>
      </div>

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
