import { useTranslation } from "react-i18next";
import { Button } from "#/components/ui/button.tsx";
import { useTranslatedText } from "#/hooks/useTranslatedText";
import Popup from "#/components/zirkusmond/general/Popup";
import type { HomepageElement } from "#/interfaces/homepage-element";
/**
 * Picks the single active pop-up from the homepage payload and renders it.
 * Only one pop-up is ever active at a time; other `HomepageElement` kinds
 * are ignored here.
 */

const DISMISSED_KEY = "zm-popup-dismissed";

const HomepagePopup = ({ elements }: { elements: HomepageElement[] }) => {
  const popup = elements.find((element) => element.type === "popupelement");

  if (!popup) return null;

  const { t } = useTranslation();
  const { title, message } = useTranslatedText(popup);

  const actions = popup.link ? (
    <Button asChild size="sm">
      <a href={popup.link} target="_blank">
        {t("popup_learn_more")}
      </a>
    </Button>
  ) : undefined;

  return (
    <Popup
      title={title}
      message={message}
      storageKey={DISMISSED_KEY}
      storageValue={String(popup.id)}
      actions={actions}
    />
  );
};

export default HomepagePopup;
