const CONSENT_KEY = "zm-cookie-consent";

export type ConsentValue = "accepted" | "declined" | null;

export const getConsent = (): ConsentValue => {
  try {
    const value = localStorage.getItem(CONSENT_KEY);
    if (value === "accepted" || value === "declined") return value;
    return null;
  } catch {
    return null;
  }
};

export const setConsent = (value: ConsentValue): void => {
  try {
    if (value === null) {
      localStorage.removeItem(CONSENT_KEY);
    } else {
      localStorage.setItem(CONSENT_KEY, value);
    }
    // Dispatch custom event so other parts of the app can react
    if (typeof window !== "undefined") {
      window.dispatchEvent(
        new CustomEvent("cookieConsentChanged", { detail: { consent: value } })
      );
    }
  } catch {
    // localStorage unavailable — consent won't persist
  }
};

export const hasConsent = (): boolean => {
  return getConsent() === "accepted";
};
