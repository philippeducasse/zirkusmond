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
import * as m from '#/paraglide/messages'

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
      <PageHeader>{m.page_payment_success_title()}</PageHeader>

      <ContentSection
        className="text-center text-white md:text-xl max-w-3xl mx-auto"
        isLoading={reservationQuery.isPending}
        skeleton={<SectionCardSkeleton lines={4} />}
      >
        {reservationQuery.isError ? (
          <SectionCard>
            <p>{m.page_payment_success_error()}</p>
          </SectionCard>
        ) : reservationQuery.data ? (
          <SectionCard className="space-y-6">
            <p>
              {m.page_payment_success_confirmation({ email: reservationQuery.data.email })}
            </p>

            {(reservationQuery.data.showTime ||
              reservationQuery.data.admissionTime) && (
              <p>
                {m.page_payment_success_timing({
                  admissionTime: reservationQuery.data.admissionTime,
                  showTime: reservationQuery.data.showTime
                })}
              </p>
            )}

            <p>
              {m.page_payment_success_directions()}{' '}
              <a
                href="https://www.openstreetmap.org/directions?from=&to=52.54226%2C13.43250"
                className="text-primary hover:underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                {m.page_payment_success_directions_link()}
              </a>
            </p>

            <p className="text-2xl">{m.page_payment_success_see_you()}</p>
          </SectionCard>
        ) : null}
        <SectionDivider type="flower" />
        <Button asChild>
          <Link to="/">{m.button_back_to_home()}</Link>
        </Button>
      </ContentSection>
    </PageContainer>
  )
}
