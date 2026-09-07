import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { XIcon } from "lucide-react";

import { Button } from "#/components/ui/button.tsx";
import { CardContent, CardHeader, CardTitle } from "#/components/ui/card.tsx";
import { cn } from "#/lib/utils.ts";
import type { PopUpElement } from "#/interfaces/homepage-element.ts";
import SectionCard from "#/components/zirkusmond/general/SectionCard";
import { useTranslatedText } from "#/hooks/useTranslatedText";

// Centered along the bottom on mobile, pinned to the bottom-right corner
// from the `sm` breakpoint up.
const POSITION_CLASSES =
  "bottom-4 left-1/2 -translate-x-1/2 sm:left-auto sm:right-4 sm:translate-x-0";

// Only one pop-up is ever active, so a single key holding the dismissed
// pop-up's id is enough — a new pop-up (different id) shows again.
const DISMISSED_KEY = "zm-popup-dismissed";

const isDismissed = (id: number): boolean => {
  try {
    return localStorage.getItem(DISMISSED_KEY) === String(id);
  } catch {
    return false;
  }
};

const PopupCard = ({ element }: { element: PopUpElement }) => {
  const { t } = useTranslation();
  const { title, message } = useTranslatedText(element);

  // Nothing renders on the server or the first client paint; the popup is
  // revealed on mount unless this viewer has already dismissed it. Keeping
  // the initial render empty avoids a hydration mismatch.
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!isDismissed(element.id)) setOpen(true);
  }, [element.id]);

  const dismiss = () => {
    setOpen(false);
    try {
      localStorage.setItem(DISMISSED_KEY, String(element.id));
    } catch {
      // localStorage unavailable — the popup just won't stay dismissed.
    }
  };

  if (!open) return null;
  return (
    <div
      role="dialog"
      aria-label={title}
      className={cn(
        "fixed z-50 w-[calc(100%-2rem)] max-w-sm bg-[url(/images/general/bg_pattern.webp)]",
        POSITION_CLASSES,
      )}
    >
      <SectionCard className="relative shadow-lg">
        <CardHeader className="flex justify-center gap-2">
          <CardTitle className="text-xl text-primary">{title}</CardTitle>
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            className="absolute top-4 right-4 [&_svg]:mr-0"
            aria-label={t("common_close")}
            onClick={dismiss}
          >
            <XIcon size={18} />
          </Button>
        </CardHeader>
        <CardContent className="flex flex-col justify-center gap-3">
          <p
            className="text-sm/relaxed md:text-base/relaxed [&_a]:underline"
            dangerouslySetInnerHTML={{ __html: message }}
          />
          {element.link && (
            <Button asChild size="sm">
              <a href={element.link} target="_blank">
                {t("popup_learn_more")}
              </a>
            </Button>
          )}
        </CardContent>
      </SectionCard>
    </div>
  );
};

export default PopupCard;
