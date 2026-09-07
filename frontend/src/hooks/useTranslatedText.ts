import { useTranslation } from "react-i18next";

import type { HomepageElementBase } from "#/interfaces/homepage-element.ts";

/**
 * Resolves the German/English copy of a homepage element for the active
 * locale. `de` is the default/fallback locale, so anything that isn't
 * English falls back to the German copy.
 */
export const useTranslatedText = (element: HomepageElementBase) => {
  const { i18n } = useTranslation();
  const isEnglish = i18n.language.startsWith("en");

  return {
    title: isEnglish ? element.titleEn : element.titleDe,
    message: isEnglish ? element.messageEn : element.messageDe,
  };
};
