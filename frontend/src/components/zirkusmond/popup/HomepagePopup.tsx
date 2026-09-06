import type { HomepageElement } from "#/interfaces/homepage-element.ts";
import PopupCard from "./PopupCard";

/**
 * Picks the single active pop-up from the homepage payload and renders it.
 * Only one pop-up is ever active at a time; other `HomepageElement` kinds
 * are ignored here.
 */
const HomepagePopup = ({ elements }: { elements: HomepageElement[] }) => {
  const popup = elements.find(
    // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition -- guard stays meaningful once the HomepageElement union grows
    (element) => element.type === "popupelement",
  );

  if (!popup) return null;

  return <PopupCard element={popup} />;
};

export default HomepagePopup;
