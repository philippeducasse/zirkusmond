import { Field, FieldLabel } from '#/components/ui/field.tsx'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '#/components/ui/select.tsx'

export interface SelectFieldProps {
  id: string
  label: string
  placeholder: string
  value: string
  onChange: (value: string) => void
  options: { value: string; label: string }[]
}

export default function SelectField({
  id,
  label,
  placeholder,
  value,
  onChange,
  options,
}: SelectFieldProps) {
  return (
    <Field orientation="responsive">
      <FieldLabel htmlFor={id} className="text-xl">
        {label}
      </FieldLabel>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger
          id={id}
          className="data-[size=default]:h-11 w-full border-primary border-2 bg-transparent text-lg hover:bg-transparent"
        >
          <SelectValue placeholder={placeholder} />
        </SelectTrigger>
        <SelectContent
          position="popper"
          align="start"
          sideOffset={4}
          className="border-primary border-2 bg-[url(/images/general/bg_pattern.webp]! bg-repeat"
        >
          {options.map((option) => (
            <SelectItem
              key={option.value}
              value={option.value}
              className="text-white text-lg"
            >
              {option.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </Field>
  )
}