import DynamicForm from '#/components/zirkusmond/form/DynamicForm'
import { buildGuestFields } from '#/components/zirkusmond/reserve/buildFormFields'
import { useTranslation } from 'react-i18next'

interface GuestFormProps {
  guestCount: number
  fieldErrors: Record<string, string>
  clearFieldError: (id: string) => void
}

export default function GuestForm({
  guestCount,
  fieldErrors,
  clearFieldError,
}: GuestFormProps) {
  const { t } = useTranslation()
  if (guestCount === 0) return null

  return (
    <div className="my-8 flex flex-col gap-6">
      {Array.from({ length: guestCount }, (_, i) => (
        <DynamicForm
          fields={buildGuestFields(fieldErrors, clearFieldError, i)}
          title={t('form_guest_number', { number: i + 1 })}
        />
      ))}
    </div>
  )
}
