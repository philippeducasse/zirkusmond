import { CardContent, CardDescription } from "#/components/ui/card.tsx";
import { useTranslation } from "react-i18next";
import SectionCard from "../general/SectionCard";

interface TimeDetailsProps {
  date: string;
  admissionTime: string;
}

export default function TimeDetails({ date, admissionTime }: TimeDetailsProps) {
  const { t } = useTranslation();
  return (
    <SectionCard>
      <CardContent className="px-6 sm:px-8 py-3 sm:py-4">
        <CardDescription className="mb-2 font-bold text-center text-base sm:text-lg text-primary">
          {date}
        </CardDescription>
        <p className="font-semibold">
          {t("show_admission")} {admissionTime}
        </p>
      </CardContent>
    </SectionCard>
  );
}
