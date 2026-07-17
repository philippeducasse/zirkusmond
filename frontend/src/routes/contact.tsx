import { createFileRoute } from '@tanstack/react-router'

import FooterSection from '#/components/zirkusmond/home/FooterSection'
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
      <FooterSection />
    </PageContainer>
  )
}
