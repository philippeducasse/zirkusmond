import { Link } from '@tanstack/react-router'

import EventCard from '#/components/common/EventCard.tsx'
import SectionDivider from '#/components/common/home/SectionDivider.tsx'
import { Button } from '#/components/ui/button.tsx'
import { MOCK_SHOWS } from '#/lib/mock-shows.ts'

interface EventsSectionProps {
  /** Renders a CTA linking to the full events page (used on the homepage). */
  showAllEventsLink?: boolean
  /** Renders a CTA linking back to the homepage (used on the events page). */
  showHomeLink?: boolean
}

export default function EventsSection({
  showAllEventsLink = false,
  showHomeLink = false,
}: EventsSectionProps) {
  return (
    <div>
      <h2 className="my-12 text-center text-3xl text-primary lg:text-5xl">
        Upcoming Shows
      </h2>
      <div className="mx-auto flex max-w-[1800px] flex-wrap justify-center gap-8 px-6">
        {MOCK_SHOWS.map((show) => (
          <Link key={show.id} to="/show/$showId" params={{ showId: show.id }}>
            <EventCard
              eventTitle={show.title}
              eventDates={show.events.map((event) => event.label)}
              eventImageUrl={show.cardImage}
            />
          </Link>
        ))}
      </div>
      {(showAllEventsLink || showHomeLink) && (
        <div className="flex justify-center pt-12">
          <Button asChild>
            {showAllEventsLink ? (
              <Link to="/events">Alle Events ansehen</Link>
            ) : (
              <Link to="/">Zurück zur Startseite</Link>
            )}
          </Button>
        </div>
      )}
      <SectionDivider type="kite" />
    </div>
  )
}
