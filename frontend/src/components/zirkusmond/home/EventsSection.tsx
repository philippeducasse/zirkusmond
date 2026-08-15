import { Link } from '@tanstack/react-router'

import EventCard from '#/components/zirkusmond/event/EventCard'
import { Button } from '#/components/ui/button.tsx'

import type { ShowCard } from '#/interfaces/show.ts'
import PageHeader from '../general/PageHeader'
import ContentSection from '../general/ContentSection'

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
    <ContentSection>
      <PageHeader>Upcoming Shows</PageHeader>

      <div className="mx-auto flex max-w-[1800px] flex-wrap justify-center gap-8 md:px-6 px-0">
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
        <div className="flex justify-center pt-24">
          <Button asChild>
            {showAllEventsLink ? (
              <Link to="/events">Alle Events ansehen</Link>
            ) : (
              <Link to="/">Zurück zur Startseite</Link>
            )}
          </Button>
        </div>
      )}
    </ContentSection>
  )
}
