import { useTranslation } from "react-i18next";

import ContentSection from "#/components/zirkusmond/general/ContentSection";
import SectionCard from "#/components/zirkusmond/general/SectionCard";

const GITHUB_REPO_URL = "https://github.com/zirkusmond/zirkusmond";

export default function OpenSource() {
  const { t } = useTranslation();

  return (
    <ContentSection className="mx-auto max-w-3xl text-center">
      <SectionCard className="space-y-4">
        <h3>Open Source</h3>
        <p>{t("page_about_open_source_content")}</p>
        <a
          href={GITHUB_REPO_URL}
          target="_blank"
          rel="noreferrer"
          className="text-xl text-primary"
        >
          {t("page_about_open_source_link")}
        </a>
      </SectionCard>
    </ContentSection>
  );
}
