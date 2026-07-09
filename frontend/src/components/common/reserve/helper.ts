import type { MockShow } from '#/lib/mock-shows.ts'

export interface SelectFieldConfig {
  kind: 'select'
  id: string
  label: string
  placeholder: string
  value: string
  onChange: (value: string) => void
  options: { value: string; label: string }[]
}

export interface NumberFieldConfig {
  kind: 'number'
  id: string
  label: string
  value: number
  onChange: (value: number) => void
  min: number
  max: number
}

export interface CheckboxFieldConfig {
  kind: 'checkbox'
  id: string
  label: string
  checked: boolean
  onChange: (checked: boolean) => void
}

export interface ButtonGroupFieldConfig {
  kind: 'button-group'
  id: string
  name: string
  options: { value: string; label: string }[]
}

export interface TextFieldConfig {
  kind: 'text'
  id: string
  label: string
  name?: string
  type?: string
  required?: boolean
}

export type DynamicFieldConfig =
  | SelectFieldConfig
  | NumberFieldConfig
  | CheckboxFieldConfig
  | ButtonGroupFieldConfig
  | TextFieldConfig

interface BuildTicketFieldsParams {
  show: MockShow
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
      options: show.events.map((event) => ({
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
      max: 10,
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
      name: 'first_name',
      required: true,
    },
    {
      kind: 'text',
      id: 'last-name',
      label: 'Last name',
      name: 'last_name',
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