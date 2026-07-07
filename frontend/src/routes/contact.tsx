import { createFileRoute } from '@tanstack/react-router'

import FooterSection from '#/components/common/home/FooterSection.tsx'
import PageContainer from '#/components/common/PageContainer.tsx'

export const Route = createFileRoute('/contact')({
  head: () => ({
    meta: [{ title: 'Zirkus Mond – Kontakt' }],
  }),
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <PageContainer>
      <FooterSection />
    </PageContainer>
  )
}
