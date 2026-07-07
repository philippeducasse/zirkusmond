import { createFileRoute } from '@tanstack/react-router'

import SectionDivider from '#/components/common/home/SectionDivider.tsx'
import PageContainer from '#/components/common/PageContainer.tsx'
import { MOCK_RENTAL_OBJECTS } from '#/lib/mock-rentals.ts'

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
    <PageContainer>
      <h2 className="py-8 text-center text-6xl">Rentals</h2>
      <div className="mb-8">
        <h3 className="text-center text-2xl md:text-4xl">
          Rent our Zirkus stuff!!
        </h3>
        <p className="py-8 text-center text-base">
          Very very cheap, very very nice.
        </p>
      </div>

      <SectionDivider type="kite" />

      <div className="my-4 grid grid-cols-1 gap-8 gap-y-16 md:grid-cols-2">
        {MOCK_RENTAL_OBJECTS.map((object) => (
          <div key={object.id} className="flex flex-col gap-3">
            <img src={object.image} alt={object.name} />
            <h3 className="text-center text-4xl">{object.name}</h3>
            <p className="text-base md:text-xl">{object.description}</p>
            <a
              href={object.link}
              target="_blank"
              rel="noreferrer"
              className="text-center text-2xl font-bold underline"
            >
              Link
            </a>
          </div>
        ))}
      </div>

      <SectionDivider type="flower" />
    </PageContainer>
  )
}
