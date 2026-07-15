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
    <Field orientation="horizontal" className="my-4 sm:my-6 flex p-3 sm:p-4 items-center">
      <FieldLabel htmlFor={id} className="text-base sm:text-lg md:text-xl">
        {label}
      </FieldLabel>
      <Checkbox
        id={id}
        checked={checked}
        onCheckedChange={(check) => onChange(check === true)}
      />
    </Field>
  )
}
