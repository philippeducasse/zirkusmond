import { createFileRoute } from '@tanstack/react-router'
import ContactSection from '#/components/zirkusmond/home/ContactSection'
import PageContainer from '#/components/zirkusmond/general/PageContainer'

export const Route = createFileRoute('/contact')({
  head: () => ({
    meta: [{ title: 'Zirkus Mond – Kontakt' }],
  }),
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <PageContainer>
      <ContactSection />
    </PageContainer>
  )
}
