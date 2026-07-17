import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/datenschutz')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <PageContainer>
      <h1 className="mb-8 text-white">IHRE BETROFFENENRECHTE</h1>
      <div className="flex flex-col gap-8">
        {SECTIONS.map((section) => (
          <section key={section.heading}>
            <h2 className="mb-2 text-primary">{section.heading}</h2>
            {section.paragraphs.map((paragraph, i) => (
              <p key={i} className="my-2">
                {paragraph}
              </p>
            ))}
            {section.list && (
              <ul className="list-disc pl-5">
                {section.list.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            )}
            {section.links && (
              <p className="my-2 flex flex-wrap gap-x-2">
                {section.links.map((link) => (
                  <a
                    key={link.href}
                    className="underline hover:text-white"
                    href={link.href}
                  >
                    {link.text}
                  </a>
                ))}
              </p>
            )}
          </section>
        ))}
      </div>
    </PageContainer>
  )
}
