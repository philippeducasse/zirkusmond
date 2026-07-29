import { createFileRoute } from '@tanstack/react-router'

import PageContainer from '#/components/zirkusmond/general/PageContainer'
import PageHeader from '#/components/zirkusmond/general/PageHeader'
import ContentSection from '#/components/zirkusmond/general/ContentSection'
import TeamGrid from '#/components/zirkusmond/general/TeamGrid'
import SectionDivider from '#/components/zirkusmond/general/SectionDivider'
import SectionCard from '#/components/zirkusmond/general/SectionCard'

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
    image: '/images/team/MnM.webp',
    name: 'Max & Marlen',
    role: 'Zirkus Directors',
  },
  {
    image: '/images/gallery/img-6.webp',
    name: 'Juan',
    role: 'Artistic Director',
  },
  {
    image: '/images/team/maria.webp',
    name: 'Maria',
    role: 'Head of Productions',
  },
  {
    image: '/images/team/valerio.webp',
    name: 'Valerio',
    role: 'Technician',
  },
  { image: '/images/team/philo_alex.jpg', name: 'Philo & Alex', role: 'IT' },
]

function About() {
  return (
    <PageContainer>
      <PageHeader>Welcome to the Moon</PageHeader>

      <ContentSection>
        <SectionCard className="p-0!">
          <img
            className="w-full"
            src="/images/gallery/img-9.webp"
            alt="Zirkus Mond Image"
          />
          <div className="p-6">
            <p>
              Der Zirkus Mond, Treffpunkt der Berliner Artistenszene,
              Veranstaltungsort für Zirkus, Theater, Tanz &amp; Konzerte erwuchs
              2018 aus den Umtrieben der Kinder Des Mondes, einem fluiden
              Kollektiv internationaler ArtistInnen, TänzerInnen &amp;
              KünstlerInnen, die zuvor über 10 Jahre im kulturellen Untergrund
              Berlins agierten und in unregelmäßigen Abständen leer stehende
              Gebäude, Brachflächen oder auch öffentliche Plätze mit Liebe und
              Leben füllten. Nun gibt es im Himmelskörper-Habitat Zirkus Mond
              jeden Monat 2 eigenproduzierte Shows und 2 Gastveranstaltungen,
              wobei durch wechselnde ArtistInnen und Konzepte jede Show ein
              Unikat ist.
            </p>
            <p>
              Die Pforten unseres Zirkuszeltes stehen offen für alle, die Lust
              haben, einen Ort der Gemeinschaft, des Schaffens und der Liebe zum
              Leben zu besuchen, zu bespielen und mitzugestalten.
            </p>
          </div>
        </SectionCard>
      </ContentSection>

      <SectionDivider type="kite" margin="small" className="mb-10" />
      <PageHeader className="mt-12 sm:mt-16">Meet the Team</PageHeader>
      <TeamGrid members={team} />
    </PageContainer>
  )
}
