import { Field, FieldLabel } from '#/components/ui/field.tsx'
import { Input } from '#/components/ui/input.tsx'

export interface TextFieldProps {
  id: string
  label: string
  name?: string
  type?: string
  required?: boolean
}

export default function TextField({
  id,
  label,
  name,
  type = 'text',
  required = false,
}: TextFieldProps) {
  return (
    <Field>
      <FieldLabel htmlFor={id} className="text-xl">
        {label}
      </FieldLabel>
      <Input
        id={id}
        name={name ?? id}
        type={type}
        required={required}
        className="h-11 text-lg"
      />
    </Field>
  )
}