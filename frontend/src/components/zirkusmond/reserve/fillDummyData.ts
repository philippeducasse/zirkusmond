import { flushSync } from "react-dom";
import type { Show } from "#/interfaces/show";
import { setFormValue } from "./reservationDraft";

interface FillDummyDataParams {
  show: Show;
  setSelectedEventId: (id: string) => void;
  setAttendeeCount: (count: number) => void;
  setNewsletter: (checked: boolean) => void;
  setCustomPrice: (price: number) => void;
}

export const fillReservationFormWithDummyData = ({
  show,
  setSelectedEventId,
  setAttendeeCount,
  setNewsletter,
  setCustomPrice,
}: FillDummyDataParams) => {
  const dummyAttendeeCount = 2;
  const firstEventId = show.upcomingEvents[0]?.id;

  // flushSync forces the guest fields to exist in the DOM before we fill them below.
  flushSync(() => {
    if (firstEventId) setSelectedEventId(firstEventId);
    setAttendeeCount(dummyAttendeeCount);
    setNewsletter(true);
    if (show.baseTicketPrice) setCustomPrice(show.baseTicketPrice);
  });

  setFormValue("firstName", "Max");
  setFormValue("lastName", "Mustermann");
  setFormValue("email", `ducassephi@hotmail.fr`);

  const dummyGuestCount = Math.min(9, Math.max(0, dummyAttendeeCount - 1));
  for (let i = 0; i < dummyGuestCount; i++) {
    setFormValue(`guest-${i}-first-name`, "Erika");
    setFormValue(`guest-${i}-last-name`, "Musterfrau");
  }
};
