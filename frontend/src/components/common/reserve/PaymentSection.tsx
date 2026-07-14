import { Button } from '#/components/ui/button.tsx'
import type { MockShow } from '#/lib/interfaces/shows.ts'
import SectionDivider from '../home/SectionDivider.tsx'

import DynamicField from './DynamicField.tsx'
import { buildNewsletterField, buildPaymentMethodField } from './helper.ts'
import SlidingScale from './SlidingScale.tsx'

interface PaymentSectionProps {
  show: MockShow
  attendeeCount: number
  customPrice: number
  setCustomPrice: (price: number) => void
  newsletter: boolean
  setNewsletter: (checked: boolean) => void
  onBack: () => void
}

export default function PaymentSection({
  show,
  attendeeCount,
  customPrice,
  setCustomPrice,
  newsletter,
  setNewsletter,
  onBack,
}: PaymentSectionProps) {
  const pricePerTicket = show.baseTicketPrice
    ? customPrice
    : (show.reservationPrice ?? 5)
  const total = attendeeCount * pricePerTicket

  const newsletterFields = buildNewsletterField({ newsletter, setNewsletter })
  const paymentMethodFields = buildPaymentMethodField()

  return (
    <>
      <div className="bg-white/[0.19]">
        {newsletterFields.map((field) => (
          <DynamicField key={field.id} field={field} />
        ))}
      </div>

      <div className="my-6">
        <h3 className="text-4xl text-primary">Payment</h3>
        <SlidingScale
          show={show}
          customPrice={customPrice}
          setCustomPrice={setCustomPrice}
        />
      </div>

      <div className="my-4 text-center">
        <h4 className="mb-3 text-2xl text-primary">
          Total Price: <span className="font-bold">{total.toFixed(2)}</span> €
        </h4>
      </div>

      <h4 className="my-12 text-center text-2xl text-primary">
        Choose Your Payment Method
      </h4>
      {paymentMethodFields.map((field) => (
        <DynamicField key={field.id} field={field} />
      ))}
      <SectionDivider type="moon" />
      <div className="mt-8 text-center">
        <Button type="button" size={'sm'} variant="secondary" onClick={onBack}>
          Back to Show
        </Button>
      </div>
    </>
  )
}
