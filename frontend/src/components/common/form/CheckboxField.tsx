import { Checkbox } from '#/components/ui/checkbox.tsx'
import { Field, FieldLabel } from '#/components/ui/field.tsx'

export interface CheckboxFieldProps {
  id: string
  label: string
  checked: boolean
  onChange: (checked: boolean) => void
}

export default function CheckboxField({
  id,
  label,
  checked,
  onChange,
}: CheckboxFieldProps) {
  return (
    <Field orientation="horizontal" className="my-6 flex p-4 items-center">
      <Checkbox
        id={id}
        checked={checked}
        onCheckedChange={(checked) => onChange(checked === true)}
      />
      <FieldLabel htmlFor={id} className="text-xl font-normal">
        {label}
      </FieldLabel>
    </Field>
  )
}
