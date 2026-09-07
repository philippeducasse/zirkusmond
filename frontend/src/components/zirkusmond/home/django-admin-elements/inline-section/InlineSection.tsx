import { Button } from "#/components/ui/button";
import { CardContent, CardTitle } from "#/components/ui/card";
import ContentSection from "#/components/zirkusmond/general/ContentSection";
import SectionCard from "#/components/zirkusmond/general/SectionCard";
import SectionDivider from "#/components/zirkusmond/general/SectionDivider";
import { useTranslatedText } from "#/hooks/useTranslatedText";
import type { InlineSectionElement } from "#/interfaces/homepage-element";
import { useTranslation } from "react-i18next";

const InlineSection = ({ element }: { element: InlineSectionElement }) => {
  const { t } = useTranslation();
  const { title, message } = useTranslatedText(element);
  return (
    <>
      <ContentSection>
        <SectionCard className="max-w-4xl mx-auto">
          <CardTitle className="text-xl text-primary text-center">
            {title}
          </CardTitle>
          <CardContent className="flex flex-col justify-center align-middle items-center gap-3 max-w-2xl mx-auto">
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
      </ContentSection>
      <SectionDivider type="kite" />
    </>
  );
};

export default InlineSection;
