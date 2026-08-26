import { Link } from '@tanstack/react-router'

import { Button } from '#/components/ui/button.tsx'
import type { Show } from '#/interfaces/show.ts'
import * as m from '#/paraglide/messages'

export function ReserveButton({ show }: { show: Show }) {
  if (show.thirdPartyReservation && show.thirdPartyReservationLink) {
    return (
      <Button asChild>
        <a
          href={show.thirdPartyReservationLink}
          target="_blank"
          rel="noreferrer"
        >
          {m.show_reserve()}
        </a>
      </Button>
    )
  }
  return (
    <Button asChild>
      <Link to="/reserve/$showId" params={{ showId: String(show.id) }}>
        {show.baseTicketPrice ? m.show_buy_tickets() : m.show_reserve()}
      </Link>
    </Button>
  )
}
