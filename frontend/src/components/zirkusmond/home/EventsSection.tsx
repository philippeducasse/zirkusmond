import { Link } from '@tanstack/react-router'

import EventCard from '#/components/zirkusmond/event/EventCard'
import SectionDivider from '#/components/zirkusmond/home/SectionDivider'
import { Button } from '#/components/ui/button.tsx'

import type { ShowCard } from '#/interfaces/show.ts'

interface EventsSectionProps {
  shows: ShowCard[]
  showAllEventsLink?: boolean
  showHomeLink?: boolean
}

export default function EventsSection({
  shows,
  showAllEventsLink = false,
  showHomeLink = false,
}: EventsSectionProps) {
  return (
    <div>
      <h2 className="my-8 sm:my-12 text-center">
        Upcoming Shows
      </h2>
      <div className="mx-auto flex max-w-[1800px] flex-wrap justify-center gap-8 px-6">
        {shows.map((show) => (
          <Link
            key={show.id}
            to="/show/$showId"
            params={{ showId: String(show.id) }}
          >
            <EventCard
              eventTitle={show.title}
              eventDates={show.eventDates}
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
