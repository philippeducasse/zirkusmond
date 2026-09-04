import { Link } from "@tanstack/react-router";

import { Button } from "#/components/ui/button.tsx";
import type { Show } from "#/interfaces/show.ts";
import { useTranslation } from "react-i18next";
import { Ticket } from "lucide-react";

export const ReserveButton = ({ show }: { show: Show }) => {
  const { t } = useTranslation();
  if (show.thirdPartyReservation && show.thirdPartyReservationLink) {
    return (
      <Button asChild>
        <a
          href={show.thirdPartyReservationLink}
          target="_blank"
          rel="noreferrer"
        >
          {/* <Ticket className="size-6" /> */}
          {t("show_reserve")}
        </a>
      </Button>
    );
  }
  return (
    <Button asChild>
      <Link to="/reserve/$showId" params={{ showId: String(show.id) }}>
        <Ticket />
        {show.baseTicketPrice ? t("show_buy_tickets") : t("show_reserve")}
      </Link>
    </Button>
  );
};
