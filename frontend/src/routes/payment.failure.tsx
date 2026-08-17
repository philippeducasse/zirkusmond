import { createFileRoute, Link } from '@tanstack/react-router'

import PageContainer from '#/components/zirkusmond/general/PageContainer'
import PageHeader from '#/components/zirkusmond/general/PageHeader'
import ContentSection from '#/components/zirkusmond/general/ContentSection'
import SectionCard from '#/components/zirkusmond/general/SectionCard'
import SectionDivider from '#/components/zirkusmond/general/SectionDivider'
import { Button } from '#/components/ui/button'

interface PaymentFailureSearch {
  paymentId?: string
  eventShowId?: number
}

function validatePaymentFailureSearch(
  search: Record<string, unknown>,
): PaymentFailureSearch {
  console.log('Raw search params:', search, 'type: ', typeof search.eventShowId)
  const result = {
    paymentId:
      typeof search.paymentId === 'string' ? search.paymentId : undefined,
    eventShowId:
      typeof search.eventShowId === 'number' ? search.eventShowId : undefined,
  }
  console.log('Validated result:', result)
  return result
}

export const Route = createFileRoute('/payment/failure')({
  validateSearch: validatePaymentFailureSearch,
  component: RouteComponent,
})

function RouteComponent() {
  const { paymentId, eventShowId } = Route.useSearch()

  return (
    <PageContainer>
      <PageHeader>Payment failed</PageHeader>

      <ContentSection className="text-center text-white max-w-2xl mx-auto">
        <SectionCard className="space-y-6">
          <h4 className="font-semibold">Sorry, something went wrong!</h4>
          {eventShowId && (
            <Button asChild>
              <Link
                to="/reserve/$showId"
                params={{ showId: String(eventShowId) }}
                className="mx-auto"
              >
                Try again?
              </Link>
            </Button>
          )}

          <p>
            If you think this has been a mistake on our side, please email:{' '}
            <a
              href={`mailto:reservation@zirkusmond.de${paymentId ? `?subject=Payment error for ${paymentId}` : ''}`}
              className="text-primary hover:underline"
            >
              reservation@zirkusmond.de
            </a>
            {paymentId && <> and mention your ID: {paymentId}</>}
          </p>
        </SectionCard>
        <SectionDivider type="flower" />
        <Button asChild>
          <Link to="/">Back to Home</Link>
        </Button>
      </ContentSection>
    </PageContainer>
  )
}
