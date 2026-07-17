import { createFileRoute } from '@tanstack/react-router'

import PageContainer from '#/components/zirkusmond/general/PageContainer'

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
  { image: 'MnM.webp', name: 'Max & Marlen', role: 'Zirkus Directors' },
  { image: 'img-6.webp', name: 'Juan', role: 'Artistic Director' },
  { image: 'maria.webp', name: 'Maria', role: 'Head of Productions' },
  { image: 'valerio.webp', name: 'Valerio', role: 'Technician' },
  { image: 'alex.webp', name: 'Alex', role: 'IT' },
]

function About() {
  return (
    <PageContainer className="px-4">
      <h1 className="display-title mb-6 sm:mb-8 text-center font-bold text-[var(--sea-ink)]">
        Welcome to the Moon
      </h1>

      <section className="island-shell rounded-2xl p-4 sm:p-6 md:p-10">
        <img
          className="mx-auto mb-6 sm:mb-8 w-full rounded-xl"
          src="/images/gallery/img-9.webp"
          alt="Zirkus Mond Image"
        />
        <p className="leading-7 sm:leading-8 text-[var(--sea-ink)]">
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
        <p className="m-0 pt-4 sm:pt-6 leading-7 sm:leading-8 text-[var(--sea-ink-soft)] sm:text-center">
          Die Pforten unseres Zirkuszeltes stehen offen für alle, die Lust
          haben, einen Ort der Gemeinschaft, des Schaffens und der Liebe zum
          Leben zu besuchen, zu bespielen und mitzugestalten.
        </p>
      </section>

      <h2 className="display-title mt-12 sm:mt-16 mb-6 sm:mb-8 text-center font-bold text-[var(--sea-ink)]">
        Meet the Team
      </h2>
      <img
        className="mx-auto mb-10 w-32"
        src="/images/gallery/deko-1.webp"
        alt=""
      />

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-5">
        {team.map((member) => (
          <div
            key={member.name}
            className="island-shell rounded-2xl p-4 text-center"
          >
            <img
              className="mx-auto aspect-square w-full rounded-xl object-cover"
              src={`/images/gallery/${member.image}`}
              alt={`Photo of ${member.name}`}
            />
            <h3 className="display-title mt-4 sm:mt-6 font-bold text-[var(--sea-ink)]">
              {member.name}
            </h3>
            <p className="mt-1 text-[var(--sea-ink-soft)]">
              {member.role}
            </p>
          </div>
        ))}
      </div>

      <img
        className="mx-auto mt-12 w-32"
        src="/images/gallery/deko-2.webp"
        alt=""
      />
    </PageContainer>
  )
}
