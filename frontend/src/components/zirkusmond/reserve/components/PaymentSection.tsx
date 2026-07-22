import { Button } from '#/components/ui/button.tsx'
import type { Show } from '#/interfaces/show.ts'
import SectionDivider from '../../general/SectionDivider.tsx'

import DynamicField from '../../form/DynamicField.tsx'
import { buildPaymentMethodField } from '../helper.ts'
import SlidingScale from './SlidingScale.tsx'

interface PaymentSectionProps {
  show: Show
  attendeeCount: number
  customPrice: number
  setCustomPrice: (price: number) => void
}

export default function PaymentSection({
  show,
  attendeeCount,
  customPrice,
  setCustomPrice,
}: PaymentSectionProps) {
  const pricePerTicket = show.baseTicketPrice
    ? customPrice
    : (show.reservationPrice ?? 5)
  const total = attendeeCount * pricePerTicket

  const paymentMethodFields = buildPaymentMethodField()

  return (
    <>
      <div className="my-4 sm:my-6">
        <h3 className="text-center">Payment</h3>
        <SlidingScale
          show={show}
          customPrice={customPrice}
          setCustomPrice={setCustomPrice}
        />
      </div>

      <div className="my-3 sm:my-4 text-center">
        <h4>
          Total Price: <span className="font-bold">{total.toFixed(2)}</span> €
        </h4>
      </div>

      <h4 className="text-center mb-12">Choose Your Payment Method</h4>
      {paymentMethodFields.map((field) => (
        <DynamicField key={field.id} field={field} />
      ))}
    </>
  )
}
