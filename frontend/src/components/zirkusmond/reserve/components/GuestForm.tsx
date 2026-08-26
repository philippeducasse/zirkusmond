import DynamicForm from '#/components/zirkusmond/form/DynamicForm'
import { buildGuestFields } from '#/components/zirkusmond/reserve/buildFormFields'
import { useTranslation } from 'react-i18next'

interface GuestFormProps {
  guestCount: number
}

export default function GuestForm({ guestCount }: GuestFormProps) {
  const { t } = useTranslation()
  if (guestCount === 0) return null

  return (
    <div className="my-8 flex flex-col gap-6">
      {Array.from({ length: guestCount }, (_, i) => (
        <DynamicForm fields={buildGuestFields(i)} title={t('form_guest_number', { number: i + 1 })} />
      ))}
    </div>
  )
}
