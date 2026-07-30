import type { Show, ShowEvent } from '#/interfaces/show.ts'
import type { ButtonGroupFieldProps } from '#/components/zirkusmond/form/ButtonGroupField'
import type { CheckboxFieldProps } from '#/components/zirkusmond/form/CheckboxField'
import type { NumberFieldProps } from '#/components/zirkusmond/form/NumberField'
import type { SelectFieldProps } from '#/components/zirkusmond/form/SelectField'
import type { TextFieldProps } from '#/components/zirkusmond/form/TextField'

export enum FieldType {
  Select = 'select',
  Number = 'number',
  Checkbox = 'checkbox',
  ButtonGroup = 'button-group',
  Text = 'text',
}

export type DynamicFieldConfig =
  | ({ fieldType: FieldType.Select } & SelectFieldProps)
  | ({ fieldType: FieldType.Number } & NumberFieldProps)
  | ({ fieldType: FieldType.Checkbox } & CheckboxFieldProps)
  | ({ fieldType: FieldType.ButtonGroup; id: string } & ButtonGroupFieldProps)
  | ({ fieldType: FieldType.Text } & TextFieldProps)

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
      fieldType: FieldType.Select,
      id: 'event',
      label: 'Event',
      placeholder: 'Termin wählen',
      value: selectedEventId,
      onChange: setSelectedEventId,
      options: show.upcomingEvents.map((event: ShowEvent) => ({
        value: event.id,
        label: event.timeAndDate,
      })),
    },
    {
      fieldType: FieldType.Number,
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
      fieldType: FieldType.Checkbox,
      id: 'newsletter',
      label: 'I would like to receive the Zirkus Mond newsletter',
      checked: newsletter,
      onChange: setNewsletter,
    },
  ]
}

export function buildPersonalInfoFields(): DynamicFieldConfig[] {
  return [
    {
      fieldType: FieldType.Text,
      id: 'first-name',
      label: 'First name',
      name: 'firstName',
      required: true,
    },
    {
      fieldType: FieldType.Text,
      id: 'last-name',
      label: 'Last name',
      name: 'lastName',
      required: true,
    },
    {
      fieldType: FieldType.Text,
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
      fieldType: FieldType.Text,
      id: `guest-${index}-first-name`,
      label: 'First name',
      name: `guest-${index}-first-name`,
      required: true,
    },
    {
      fieldType: FieldType.Text,
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
      fieldType: FieldType.ButtonGroup,
      id: 'payment-method',
      name: 'payment-method',
      options: [
        { value: 'paypal', label: 'PayPal' },
        { value: 'stripe', label: 'Bank Card' },
      ],
    },
  ]
}
