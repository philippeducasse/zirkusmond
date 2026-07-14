import type { Show } from '#/interfaces/show.ts'
import type { ButtonGroupFieldProps } from '#/components/common/form/ButtonGroupField.tsx'
import type { CheckboxFieldProps } from '#/components/common/form/CheckboxField.tsx'
import type { NumberFieldProps } from '#/components/common/form/NumberField.tsx'
import type { SelectFieldProps } from '#/components/common/form/SelectField.tsx'
import type { TextFieldProps } from '#/components/common/form/TextField.tsx'

export type DynamicFieldConfig =
  | ({ kind: 'select' } & SelectFieldProps)
  | ({ kind: 'number' } & NumberFieldProps)
  | ({ kind: 'checkbox' } & CheckboxFieldProps)
  | ({ kind: 'button-group'; id: string } & ButtonGroupFieldProps)
  | ({ kind: 'text' } & TextFieldProps)

interface BuildTicketFieldsParams {
  show: Show
  selectedEventId: string
  setSelectedEventId: (id: string) => void
  attendeeCount: number
  setAttendeeCount: (count: number) => void
}

export function buildTicketFields({
  show,
  selectedEventId,
  setSelectedEventId,
  attendeeCount,
  setAttendeeCount,
}: BuildTicketFieldsParams): DynamicFieldConfig[] {
  return [
    {
      kind: 'select',
      id: 'event',
      label: 'Event',
      placeholder: 'Termin wählen',
      value: selectedEventId,
      onChange: setSelectedEventId,
      options: show.upcomingEvents.map((event) => ({
        value: event.id,
        label: event.label,
      })),
    },
    {
      kind: 'number',
      id: 'attendee-count',
      label: 'Tickets',
      value: attendeeCount,
      onChange: (count) => setAttendeeCount(Math.min(10, Math.max(1, count))),
      min: 1,
      max: 100,
    },
  ]
}

interface BuildNewsletterFieldParams {
  newsletter: boolean
  setNewsletter: (checked: boolean) => void
}

export function buildNewsletterField({
  newsletter,
  setNewsletter,
}: BuildNewsletterFieldParams): DynamicFieldConfig[] {
  return [
    {
      kind: 'checkbox',
      id: 'newsletter',
      label: 'I would like to receive the Zirkus Mond newsletter.',
      checked: newsletter,
      onChange: setNewsletter,
    },
  ]
}

export function buildPersonalInfoFields(): DynamicFieldConfig[] {
  return [
    {
      kind: 'text',
      id: 'first-name',
      label: 'First name',
      name: 'firstName',
      required: true,
    },
    {
      kind: 'text',
      id: 'last-name',
      label: 'Last name',
      name: 'lastName',
      required: true,
    },
    {
      kind: 'text',
      id: 'email',
      label: 'Email',
      name: 'email',
      type: 'email',
      required: true,
    },
  ]
}

export function buildGuestFields(index: number): DynamicFieldConfig[] {
  return [
    {
      kind: 'text',
      id: `guest-${index}-first-name`,
      label: 'First name',
      name: `guest-${index}-first-name`,
      required: true,
    },
    {
      kind: 'text',
      id: `guest-${index}-last-name`,
      label: 'Last name',
      name: `guest-${index}-last-name`,
      required: true,
    },
  ]
}

export function buildPaymentMethodField(): DynamicFieldConfig[] {
  return [
    {
      kind: 'button-group',
      id: 'payment-method',
      name: 'payment-method',
      options: [
        { value: 'paypal', label: 'PayPal' },
        { value: 'stripe', label: 'Bank Card' },
      ],
    },
  ]
}
