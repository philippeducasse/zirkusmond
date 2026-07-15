import { ChevronDownIcon, ChevronUpIcon } from 'lucide-react'

import { Field, FieldLabel } from '#/components/ui/field.tsx'
import { Input } from '#/components/ui/input.tsx'

export interface NumberFieldProps {
  id: string
  label: string
  value: number
  onChange: (value: number) => void
  min: number
  max: number
}

export default function NumberField({
  id,
  label,
  value,
  onChange,
  min,
  max,
}: NumberFieldProps) {
  return (
    <Field orientation="responsive">
      <FieldLabel htmlFor={id} className="text-base sm:text-lg md:text-xl">
        {label}
      </FieldLabel>
      <div className="relative w-16">
        <Input
          id={id}
          type="number"
          min={min}
          max={max}
          value={value}
          onChange={(e) => onChange(Number(e.target.value) || min)}
          className="h-10 sm:h-11 w-full pr-7 text-base! sm:text-lg! text-white [-moz-appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
        />
        <div className="absolute inset-y-0 right-0 flex w-6 flex-col border-l-2 border-primary">
          <button
            type="button"
            aria-label="Increase"
            onClick={() => onChange(Math.min(max, value + 1))}
            disabled={value >= max}
            className="flex flex-1 items-center justify-center border-b border-primary bg-lagoon text-primary transition-colors hover:bg-primary hover:text-primary-foreground disabled:pointer-events-none disabled:opacity-50"
          >
            <ChevronUpIcon className="size-4" />
          </button>
          <button
            type="button"
            aria-label="Decrease"
            onClick={() => onChange(Math.max(min, value - 1))}
            disabled={value <= min}
            className="flex flex-1 items-center justify-center bg-lagoon text-primary transition-colors hover:bg-primary hover:text-primary-foreground disabled:pointer-events-none disabled:opacity-50"
          >
            <ChevronDownIcon className="size-4" />
          </button>
        </div>
      </div>
    </Field>
  )
}