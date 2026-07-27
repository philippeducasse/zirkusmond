import { createFileRoute, Link } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'

import PageContainer from '#/components/zirkusmond/general/PageContainer'
import PageHeader from '#/components/zirkusmond/general/PageHeader'
import ContentSection from '#/components/zirkusmond/general/ContentSection'
import { reservationDetailQueryOptions } from '#/lib/api'
import { Button } from '#/components/ui/button'
import SectionCard from '#/components/zirkusmond/general/SectionCard'
import SectionCardSkeleton from '#/components/zirkusmond/general/SectionCardSkeleton'
import SectionDivider from '#/components/zirkusmond/general/SectionDivider'

interface PaymentSuccessSearch {
  reservationId: string
}

function validatePaymentSuccessSearch(
  search: Record<string, unknown>,
): PaymentSuccessSearch {
  return {
    reservationId:
      typeof search.reservationId === 'string' ? search.reservationId : '',
  }
}

export const Route = createFileRoute('/payment/success')({
  validateSearch: validatePaymentSuccessSearch,
  component: RouteComponent,
})

function RouteComponent() {
  const { reservationId } = Route.useSearch()

  const reservationQuery = useQuery(
    reservationDetailQueryOptions(reservationId),
  )

  return (
    <PageContainer>
      <PageHeader>Thank you for your reservation</PageHeader>

      {reservationQuery.isPending ? (
        <ContentSection className="text-center text-white md:text-xl max-w-3xl mx-auto">
          <SectionCardSkeleton lines={4} />
        </ContentSection>
      ) : reservationQuery.isError ? (
        <ContentSection className="text-center text-white md:text-xl max-w-3xl mx-auto">
          <SectionCard>
            <p>Error loading reservation details. Please contact support.</p>
          </SectionCard>
        </ContentSection>
      ) : (
        <ContentSection className="text-center text-white md:text-xl max-w-3xl mx-auto">
          <SectionCard className="space-y-6">
            <p className="text-pretty">
              A confirmation email has been sent to{' '}
              <span className="font-bold text-primary">
                {reservationQuery.data.email}
              </span>
              . Please check your spam folder as well. We look forward to seeing
              you!
            </p>

            {(reservationQuery.data.showTime ||
              reservationQuery.data.admissionTime) && (
              <p className="text-pretty">
                We open our gates at{' '}
                <span className="font-bold text-primary">
                  {reservationQuery.data.admissionTime}
                </span>
                , the show will start at{' '}
                <span className="font-bold text-primary">
                  {reservationQuery.data.showTime}
                </span>
              </p>
            )}

            <p className="text-pretty">
              If you have not been to our tent yet, here are{' '}
              <a
                href="https://www.openstreetmap.org/directions?from=&to=52.54226%2C13.43250"
                className="text-primary hover:underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                directions
              </a>
            </p>

            <p className="text-2xl text-pretty">
              See you at Zirkus Mond and have fun!
            </p>
          </SectionCard>
          <SectionDivider type="flower" />
          <Button asChild>
            <Link to="/">Back to Home</Link>
          </Button>
        </ContentSection>
      )}
    </PageContainer>
  )
}
