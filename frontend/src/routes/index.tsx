import EventCard from '#/components/common/EventCard'
import { Button } from '#/components/ui/button'
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/')({ component: App })

function App() {
  return (
    <div className="flex h-screen w-full mt-12">
      <EventCard
        eventTitle="Open Stage - 2026 - Vol. III"
        eventDates={[
          'Sunday 05.07.26 at 20:00',
          'Sunday 05.07.26 at 20:00',
          'Sunday 05.07.26 at 20:00',
        ]}
        eventImageUrl="/images/team/maria.webp"
      />
      <EventCard
        eventTitle="Open Stage - 2026 - Vol. III"
        eventDates={[
          'Sunday 05.07.26 at 20:00',
          'Sunday 05.07.26 at 20:00',
          'Sunday 05.07.26 at 20:00',
        ]}
        eventImageUrl="/images/team/maria.webp"
      />
      <Button className="m-auto">Tickets Kaufen</Button>
    </div>
  )
}
