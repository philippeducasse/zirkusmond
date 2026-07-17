import { createFileRoute } from '@tanstack/react-router'

import PageContainer from '#/components/zirkusmond/general/PageContainer'

export const Route = createFileRoute('/impressum')({
  head: () => ({
    meta: [{ title: 'Zirkus Mond - Impressum' }],
  }),
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <PageContainer className="text-center lg:text-lg">
      <h2 className="mb-5 text-white">Impressum</h2>
      <p>
        Kultstätte 58 GmbH
        <br />
        Geschäftsführer Max Mohr
        <br />
        Körtestraße 38
        <br />
        10967 Berlin
        <br />
        <br />
        Tel. Max Mohr: 015770280810
        <br />
        E-Mail: maxmohr@posteo.de
        <br />
        <br />
        Steuer-Nr.: 37 / 406 / 50011
        <br />
        Steuer-ID: DE65 812 397 023
        <br />
        USt-IdNr: DE319431419
        <br />
        Finanzamt für Körperschaften II
        <br />
        Handelsregister-Nr.: HRB 164783B
      </p>
    </PageContainer>
  )
}
