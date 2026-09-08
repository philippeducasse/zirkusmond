import { createFileRoute } from "@tanstack/react-router";
import { useSuspenseQuery } from "@tanstack/react-query";

import EventsSection from "#/components/zirkusmond/home/EventsSection";
// import GallerySection from '#/components/zirkusmond/home/GallerySection'
import Hero from "#/components/zirkusmond/home/Hero";
import { homepageQueryOptions } from "#/lib/api.ts";
import PageContainer from "#/components/zirkusmond/general/PageContainer";
import ContactSection from "#/components/zirkusmond/home/ContactSection";
import HomepagePopup from "#/components/zirkusmond/home/django-admin-elements/popup/HomepagePopup";
import InlineSection from "#/components/zirkusmond/home/django-admin-elements/inline-section/InlineSection";
import type { InlineSectionElement } from "#/interfaces/homepage-element";

const App = () => {
  // TanStack Query: resolves instantly from the cache filled by the loader
  // (no loading state needed); would suspend only on a cache miss.
  const { data } = useSuspenseQuery(homepageQueryOptions);
  const preShowSection = data.additionalElements.find(
    (el): el is InlineSectionElement => el.type === "preshowselement",
  );
  const postShowSection = data.additionalElements.find(
    (el): el is InlineSectionElement => el.type === "postshowselement",
  );

  return (
    <>
      <Hero />
      <PageContainer className="pt-0">
        {import.meta.env.DEV && (
          <div className="fixed bottom-4 right-4 z-50">
            <button
              type="button"
              onClick={() => {
                throw new Error("Sentry Frontend Test Error");
              }}
              className="rounded bg-red-600 px-4 py-2 text-white shadow-lg hover:bg-red-700"
            >
              Test Sentry Error
            </button>
          </div>
        )}
        {preShowSection && <InlineSection element={preShowSection} />}
        <EventsSection shows={data.upcomingShows} showAllEventsLink />
        {/* <GallerySection /> */}
        {postShowSection && <InlineSection element={postShowSection} />}

        <ContactSection />
      </PageContainer>
      <HomepagePopup elements={data.additionalElements} />
    </>
  );
};

export const Route = createFileRoute("/")({
  // TanStack Query: `ensureQueryData` fetches into the cache unless the data
  // is already there. On the server this runs during SSR and the result is
  // dehydrated into the HTML; useSuspenseQuery below then reads it from cache.
  loader: ({ context: { queryClient } }) =>
    queryClient.ensureQueryData(homepageQueryOptions),
  head: () => ({
    meta: [
      { title: "Zirkus Mond" },
      {
        name: "description",
        content:
          "Zirkus Mond – Dein Zirkus in Berlin! Entdecke unser Programm: Live Shows, Events, Community und zeitgenössische Zirkuskunst im Herzen Berlins.",
      },
      {
        name: "keywords",
        content:
          "Zirkus Mond Berlin, Zirkus Mond Shows, Zirkus Mond Events, Zirkus Mond Tickets, Live Shows Berlin, Kulturveranstaltungen Berlin, zeitgenössischer Zirkus Berlin, unabhängiger Zirkus Berlin",
      },
    ],
  }),
  component: App,
});
