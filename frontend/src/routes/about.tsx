import { createFileRoute } from '@tanstack/react-router'

import PageContainer from '#/components/zirkusmond/general/PageContainer'
import PageHeader from '#/components/zirkusmond/general/PageHeader'
import ContentSection from '#/components/zirkusmond/general/ContentSection'
import TeamGrid from '#/components/zirkusmond/general/TeamGrid'
import SectionDivider from '#/components/zirkusmond/general/SectionDivider'

export const Route = createFileRoute('/about')({
  head: () => ({
    meta: [
      { title: 'Zirkus Mond – Über uns' },
      {
        name: 'description',
        content:
          'Lerne das Team hinter Zirkus Mond kennen – ein Kollektiv internationaler Artist:innen, Tänzer:innen und Künstler:innen in Berlin.',
      },
      {
        name: 'keywords',
        content:
          'Zirkus Mond Artist:innen, Artist:innen Berlin, Zirkus Artist:innen, Performance Ensemble, internationale Artist:innen, lokale Künstler:innen, Zirkuskollektiv, Ensemble, interdisziplinäre Kunst, experimentelle Kunst, unabhängige Szene Berlin, Artist, Artistin, Zirkusartist, Zirkusartistin, Performer, Performer:in, Akrobat, Akrobatin, Luftartist, Kunstszene Berlin',
      },
    ],
  }),
  component: About,
})

const team = [
  {
    image: '/images/gallery/MnM.webp',
    name: 'Max & Marlen',
    role: 'Zirkus Directors',
  },
  {
    image: '/images/gallery/img-6.webp',
    name: 'Juan',
    role: 'Artistic Director',
  },
  {
    image: '/images/gallery/maria.webp',
    name: 'Maria',
    role: 'Head of Productions',
  },
  {
    image: '/images/gallery/valerio.webp',
    name: 'Valerio',
    role: 'Technician',
  },
  { image: '/images/gallery/alex.webp', name: 'Alex', role: 'IT' },
]

function About() {
  return (
    <PageContainer>
      <PageHeader>Welcome to the Moon</PageHeader>

      <ContentSection>
        <img
          className="mx-auto mb-6 sm:mb-8 w-full rounded-xl"
          src="/images/gallery/img-9.webp"
          alt="Zirkus Mond Image"
        />
        <p className="leading-7 sm:leading-8 text-(--sea-ink)">
          Der Zirkus Mond, Treffpunkt der Berliner Artistenszene,
          Veranstaltungsort für Zirkus, Theater, Tanz &amp; Konzerte erwuchs
          2018 aus den Umtrieben der Kinder Des Mondes, einem fluiden Kollektiv
          internationaler ArtistInnen, TänzerInnen &amp; KünstlerInnen, die
          zuvor über 10 Jahre im kulturellen Untergrund Berlins agierten und in
          unregelmäßigen Abständen leer stehende Gebäude, Brachflächen oder auch
          öffentliche Plätze mit Liebe und Leben füllten. Nun gibt es im
          Himmelskörper-Habitat Zirkus Mond jeden Monat 2 eigenproduzierte Shows
          und 2 Gastveranstaltungen, wobei durch wechselnde ArtistInnen und
          Konzepte jede Show ein Unikat ist.
        </p>
        <p className="m-0 pt-4 sm:pt-6 leading-7 sm:leading-8 text-(--sea-ink-soft) sm:text-center">
          Die Pforten unseres Zirkuszeltes stehen offen für alle, die Lust
          haben, einen Ort der Gemeinschaft, des Schaffens und der Liebe zum
          Leben zu besuchen, zu bespielen und mitzugestalten.
        </p>
      </ContentSection>

      <PageHeader className="mt-12 sm:mt-16">Meet the Team</PageHeader>

      <SectionDivider type="kite" margin="small" className="mb-10" />

      <TeamGrid members={team} />
    </PageContainer>
  )
}
