import { Field, FieldLabel } from '#/components/ui/field.tsx'
import { Input } from '#/components/ui/input.tsx'

interface FormFieldProps {
  id: string
  label: string
  name?: string
  type?: string
  required?: boolean
  value?: string | number
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void
}

export default function FormField({
  id,
  label,
  name,
  type = 'text',
  required = false,
  value,
  onChange,
}: FormFieldProps) {
  return (
    <Field>
      <FieldLabel htmlFor={id}>{label}</FieldLabel>
      <Input
        id={id}
        name={name || id}
        type={type}
        required={required}
        value={value}
        onChange={onChange}
      />
    </Field>
  )
}