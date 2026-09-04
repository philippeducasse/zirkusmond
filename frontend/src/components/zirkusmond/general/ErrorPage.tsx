import { Link } from "@tanstack/react-router";
import { useTranslation } from "react-i18next";
import { Home } from "lucide-react";

import PageContainer from "#/components/zirkusmond/general/PageContainer";
import PageHeader from "#/components/zirkusmond/general/PageHeader";
import ContentSection from "#/components/zirkusmond/general/ContentSection";
import SectionCard from "#/components/zirkusmond/general/SectionCard";
import SectionDivider from "#/components/zirkusmond/general/SectionDivider";
import { Button } from "#/components/ui/button";

const ErrorPage = ({ error }: { error: Error }) => {
  const { t } = useTranslation();

  return (
    <PageContainer>
      <PageHeader>{t("error_generic")}</PageHeader>

      <ContentSection className="text-center text-white max-w-2xl mx-auto">
        <SectionCard className="space-y-6">
          <h4 className="font-semibold">{t("error_generic_title")}</h4>

          <p className="text-gray-300">
            {error instanceof Error ? error.message : t("error_generic")}
          </p>
        </SectionCard>
        <SectionDivider type="flower" />
        <Button asChild>
          <Link to="/" className="inline-flex items-center gap-2">
            <Home className="w-4 h-4" />
            {t("button_back_to_home")}
          </Link>
        </Button>
      </ContentSection>
    </PageContainer>
  );
};

export default ErrorPage;
