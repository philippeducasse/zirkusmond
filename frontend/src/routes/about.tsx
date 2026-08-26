import { createFileRoute } from '@tanstack/react-router'

import PageContainer from '#/components/zirkusmond/general/PageContainer'
import PageHeader from '#/components/zirkusmond/general/PageHeader'
import ContentSection from '#/components/zirkusmond/general/ContentSection'
import TeamGrid from '#/components/zirkusmond/general/TeamGrid'
import SectionDivider from '#/components/zirkusmond/general/SectionDivider'
import SectionCard from '#/components/zirkusmond/general/SectionCard'
import * as m from '#/paraglide/messages'

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
    role: m.role_zirkus_directors(),
  },
  {
    image: '/images/gallery/img-6.webp',
    name: 'Juan',
    role: m.role_artistic_director(),
  },
  {
    image: '/images/team/maria.webp',
    name: 'Maria',
    role: m.role_head_of_productions(),
  },
  {
    image: '/images/team/valerio.webp',
    name: 'Valerio',
    role: m.role_technician(),
  },
  { image: '/images/team/philo_alex.jpg', name: 'Philo & Alex', role: m.role_it() },
]

function About() {
  return (
    <PageContainer>
      <PageHeader>{m.page_about_title()}</PageHeader>

      <ContentSection>
        <SectionCard className="p-0!">
          <img
            className="w-full"
            src="/images/gallery/img-9.webp"
            alt="Zirkus Mond Image"
          />
          <div className="p-6 md:px-24 md:pb-12">
            <p>
              {m.page_about_content_p1()}
            </p>
            <p>
              {m.page_about_content_p2()}
            </p>
          </div>
        </SectionCard>
      </ContentSection>

      <SectionDivider type="kite" margin="small" className="mb-10" />
      <PageHeader className="mt-12 sm:mt-16">{m.page_about_team()}</PageHeader>
      <TeamGrid members={team} />
    </PageContainer>
  )
}
