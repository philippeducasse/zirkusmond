import DynamicForm from '#/components/common/reserve/DynamicForm.tsx'
import { buildGuestFields } from '#/components/common/reserve/helper.ts'

interface GuestFormProps {
  guestCount: number
}

export default function GuestForm({ guestCount }: GuestFormProps) {
  if (guestCount === 0) return null

  return (
    <div className="my-8 flex flex-col gap-6">
      {Array.from({ length: guestCount }, (_, i) => (
        <DynamicForm fields={buildGuestFields(i)} title={`Guest ${i + 1}`} />
      ))}
    </div>
  )
}
