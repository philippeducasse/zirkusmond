import { createFileRoute } from "@tanstack/react-router";
import ContactSection from "#/components/zirkusmond/home/ContactSection";
import PageContainer from "#/components/zirkusmond/general/PageContainer";

const RouteComponent = () => {
  return (
    <PageContainer>
      <ContactSection />
    </PageContainer>
  );
};

export const Route = createFileRoute("/contact")({
  head: () => ({
    meta: [{ title: "Zirkus Mond – Kontakt" }],
  }),
  component: RouteComponent,
});
