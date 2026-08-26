import DynamicForm from '#/components/zirkusmond/form/DynamicForm'
import { buildGuestFields } from '#/components/zirkusmond/reserve/buildFormFields'
import * as m from '#/paraglide/messages'

interface GuestFormProps {
  guestCount: number
}

export default function GuestForm({ guestCount }: GuestFormProps) {
  if (guestCount === 0) return null

  return (
    <div className="my-8 flex flex-col gap-6">
      {Array.from({ length: guestCount }, (_, i) => (
        <DynamicForm fields={buildGuestFields(i)} title={m.form_guest_number({ number: i + 1 })} />
      ))}
    </div>
  )
}
