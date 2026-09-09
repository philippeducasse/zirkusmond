import { useEffect, useState } from "react";
import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { XIcon } from "lucide-react";

import { Button } from "#/components/ui/button.tsx";
import { CardContent, CardHeader, CardTitle } from "#/components/ui/card.tsx";
import { cn } from "#/lib/utils.ts";
import SectionCard from "#/components/zirkusmond/general/SectionCard";

const POSITION_CLASSES =
  "bottom-4 left-1/2 -translate-x-1/2 sm:left-auto sm:right-4 sm:translate-x-0";

interface PopupProps {
  title: string;
  message: string;
  storageKey: string;
  storageValue: string;
  showCloseButton?: boolean;
  actions?: ReactNode;
  shouldShow?: () => boolean;
}

/**
 * Generic popup component that handles localStorage-based dismissal and
 * hydration-safe rendering. Used by both Django-driven popups and
 * cookie consent banner.
 */
const Popup = ({
  title,
  message,
  storageKey,
  storageValue,
  showCloseButton = true,
  actions,
  shouldShow,
}: PopupProps) => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const isDismissed = () => {
      try {
        return localStorage.getItem(storageKey) === storageValue;
      } catch {
        return false;
      }
    };

    const customCheck = shouldShow ? shouldShow() : true;
    if (!isDismissed() && customCheck) setOpen(true);
  }, [storageKey, storageValue, shouldShow]);

  const dismiss = () => {
    setOpen(false);
    try {
      localStorage.setItem(storageKey, storageValue);
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
          {showCloseButton && (
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
          )}
        </CardHeader>
        <CardContent className="flex flex-col justify-center gap-3">
          <p
            className="text-sm/relaxed md:text-base/relaxed [&_a]:underline"
            dangerouslySetInnerHTML={{ __html: message }}
          />
          {actions}
        </CardContent>
      </SectionCard>
    </div>
  );
};

export default Popup;
