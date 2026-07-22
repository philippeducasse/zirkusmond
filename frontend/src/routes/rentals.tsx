import { createFileRoute } from '@tanstack/react-router'

import SectionDivider from '#/components/zirkusmond/general/SectionDivider'
import PageContainer from '#/components/zirkusmond/general/PageContainer'
import PageHeader from '#/components/zirkusmond/general/PageHeader'
import ContentSection from '#/components/zirkusmond/general/ContentSection'
import { MOCK_RENTAL_OBJECTS } from '#/interfaces/rentals'

export const Route = createFileRoute('/rentals')({
  head: () => ({
    meta: [
      { title: 'Zirkus Mond – Zirkuszelt & Equipment mieten' },
      {
        name: 'description',
        content:
          'Miete Zirkuszelt, Bühne und Equipment von Zirkus Mond Berlin – die alternative Eventlocation und Kulturraum für dein Event.',
      },
    ],
  }),
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <PageContainer className="px-4">
      <PageHeader>Rentals</PageHeader>

      <ContentSection className="mb-6 sm:mb-8">
        <h3 className="text-center">Rent our Zirkus stuff!!</h3>
        <p className="py-6 sm:py-8 text-center">
          Very very cheap, very very nice.
        </p>
      </ContentSection>

      <SectionDivider type="kite" />

      <div className="my-4 grid grid-cols-1 gap-8 gap-y-16 md:grid-cols-2">
        {MOCK_RENTAL_OBJECTS.map((object) => (
          <ContentSection key={object.id} className="flex flex-col gap-3">
            <img src={object.image} alt={object.name} className="rounded-xl" />
            <h3 className="text-center text-(--sea-ink)">{object.name}</h3>
            <p className="text-(--sea-ink)">{object.description}</p>
            <a
              href={object.link}
              target="_blank"
              rel="noreferrer"
              className="text-center text-lg sm:text-xl md:text-2xl font-bold underline text-(--sea-ink)"
            >
              Link
            </a>
          </ContentSection>
        ))}
      </div>

      <SectionDivider type="flower" />
    </PageContainer>
  )
}
