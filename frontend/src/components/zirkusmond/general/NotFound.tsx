import { Link } from "@tanstack/react-router";

import PageContainer from "#/components/zirkusmond/general/PageContainer";
import PageHeader from "#/components/zirkusmond/general/PageHeader";
import ContentSection from "#/components/zirkusmond/general/ContentSection";
import SectionCard from "#/components/zirkusmond/general/SectionCard";
import { Button } from "#/components/ui/button.tsx";
import { useTranslation } from "react-i18next";

interface NotFoundProps {
  entityName?: string;
}

export default function NotFound({ entityName = "Page" }: NotFoundProps) {
  const { t } = useTranslation();
  return (
    <PageContainer className="flex flex-col items-center gap-6 px-4 text-center">
      <PageHeader>{t("not_found_title", { entity: entityName })}</PageHeader>
      <ContentSection>
        <SectionCard>
          <p>{t("not_found_message", { entity: entityName.toLowerCase() })}</p>
          <Button
            variant={"secondary"}
            asChild
            className=" w-full md:w-1/2 mx-auto mt-10"
          >
            <Link to="/">{t("common_home")}</Link>
          </Button>
        </SectionCard>
      </ContentSection>
    </PageContainer>
  );
}
