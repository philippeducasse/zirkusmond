import { useTranslation } from "react-i18next";
import { Button } from "#/components/ui/button.tsx";
import Popup from "#/components/zirkusmond/general/Popup";
import { getConsent, setConsent } from "#/lib/cookieConsent";

const CONSENT_STORAGE_KEY = "zm-cookie-consent";

const CookieConsentBanner = () => {
  const { t } = useTranslation();

  const actions = (dismiss: () => void) => {
    const handleAccept = () => {
      setConsent("accepted");
      dismiss();
    };

    const handleDecline = () => {
      setConsent("declined");
      dismiss();
    };

    return (
      <div className="flex flex-col sm:flex-row gap-2">
        <Button
          onClick={handleDecline}
          size="sm"
          variant="outline"
          className="flex-1 text-white"
        >
          {t("cookie_banner_decline")}
        </Button>
        <Button onClick={handleAccept} size="sm" className="flex-1">
          {t("cookie_banner_accept")}
        </Button>
      </div>
    );
  };

  return (
    <Popup
      title={t("cookie_banner_title")}
      message={t("cookie_banner_message")}
      storageKey={CONSENT_STORAGE_KEY}
      storageValue="dismissed"
      showCloseButton={false}
      actions={actions}
      shouldShow={() => getConsent() === null}
    />
  );
};

export default CookieConsentBanner;
