import { Button } from '#/components/ui/button.tsx'
import { Checkbox } from '#/components/ui/checkbox.tsx'
import { Field, FieldLabel } from '#/components/ui/field.tsx'
import type { MockShow } from '#/lib/mock-shows.ts'
import SectionDivider from '../home/SectionDivider.tsx'

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

  return (
    <>
      <div className="bg-white/[0.19]">
        <Field orientation="horizontal" className="my-6 flex p-4 items-center">
          <Checkbox
            id="newsletter"
            checked={newsletter}
            onCheckedChange={(checked) => setNewsletter(checked === true)}
          />
          <FieldLabel htmlFor="newsletter" className="font-normal">
            I would like to receive the Zirkus Mond newsletter.
          </FieldLabel>
        </Field>
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
      <div className="flex flex-col justify-evenly gap-4 md:flex-row">
        <div className="my-2 mx-auto md:w-auto w-4/5">
          <Button
            type="submit"
            name="payment-method"
            value="paypal"
            className="w-full"
          >
            PayPal
          </Button>
        </div>
        <div className="my-2 mx-auto md:w-auto w-4/5">
          <Button
            type="submit"
            name="payment-method"
            value="stripe"
            className="w-full"
          >
            Bank Card
          </Button>
        </div>
      </div>
      <SectionDivider type="moon" />
      <div className="mt-8 text-center">
        <Button type="button" size={'sm'} variant="secondary" onClick={onBack}>
          Back to Show
        </Button>
      </div>
    </>
  )
}
