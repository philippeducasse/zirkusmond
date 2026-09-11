import { createFileRoute } from "@tanstack/react-router";

import PageContainer from "#/components/zirkusmond/general/PageContainer";
import PageHeader from "#/components/zirkusmond/general/PageHeader";
import ContentSection from "#/components/zirkusmond/general/ContentSection";
import TeamGrid from "#/components/zirkusmond/general/TeamGrid";
import SectionDivider from "#/components/zirkusmond/general/SectionDivider";
import SectionCard from "#/components/zirkusmond/general/SectionCard";
import { useTranslation } from "react-i18next";

const GITHUB_REPO_URL = "https://github.com/philippeducasse/zirkusmond";

const About = () => {
  const { t } = useTranslation();

  const team = [
    {
      image: "/images/team/MnM.webp",
      name: "Max & Marlen",
      role: t("role_zirkus_directors"),
    },
    {
      image: "/images/gallery/img-6.webp",
      name: "Juan",
      role: t("role_artistic_director"),
    },
    {
      image: "/images/team/maria.webp",
      name: "Maria",
      role: t("role_head_of_productions"),
    },
    {
      image: "/images/team/valerio.webp",
      name: "Valerio",
      role: t("role_technician"),
    },
    {
      image: "/images/team/philo_alex.jpg",
      name: "Philo & Alex",
      role: t("role_it"),
    },
  ];

  return (
    <PageContainer>
      <PageHeader>{t("page_about_title")}</PageHeader>

      <ContentSection>
        <SectionCard className="p-0!">
          <img
            className="w-full"
            src="/images/gallery/img-9.webp"
            alt="Zirkus Mond Image"
          />
          <div className="p-6 md:px-24 md:pb-12">
            <p>{t("page_about_content_p1")}</p>
            <p>{t("page_about_content_p2")}</p>
          </div>
        </SectionCard>
      </ContentSection>

      <SectionDivider type="kite" margin="small" className="mb-10" />
      <PageHeader className="mt-12 sm:mt-16">{t("page_about_team")}</PageHeader>
      <TeamGrid members={team} />

      <SectionDivider type="flower" />
      <PageHeader>{t("page_about_open_source_title")}</PageHeader>
      <ContentSection className="text-center max-w-3xl mx-auto">
        <SectionCard className="space-y-4">
          <p>{t("page_about_open_source_content")}</p>
          <a
            href={GITHUB_REPO_URL}
            target="_blank"
            rel="noreferrer"
            className="text-base text-primary"
          >
            {t("page_about_open_source_link")}
          </a>
        </SectionCard>
      </ContentSection>
    </PageContainer>
  );
};

export const Route = createFileRoute("/about")({
  head: () => ({
    meta: [
      { title: "Zirkus Mond – Über uns" },
      {
        name: "description",
        content:
          "Lerne das Team hinter Zirkus Mond kennen – ein Kollektiv internationaler Artist:innen, Tänzer:innen und Künstler:innen in Berlin.",
      },
      {
        name: "keywords",
        content:
          "Zirkus Mond Artist:innen, Artist:innen Berlin, Zirkus Artist:innen, Performance Ensemble, internationale Artist:innen, lokale Künstler:innen, Zirkuskollektiv, Ensemble, interdisziplinäre Kunst, experimentelle Kunst, unabhängige Szene Berlin, Artist, Artistin, Zirkusartist, Zirkusartistin, Performer, Performer:in, Akrobat, Akrobatin, Luftartist, Kunstszene Berlin",
      },
    ],
  }),
  component: About,
});
