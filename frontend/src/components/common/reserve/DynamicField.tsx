import { ChevronDownIcon, ChevronUpIcon } from 'lucide-react'

import { Button } from '#/components/ui/button.tsx'
import { Checkbox } from '#/components/ui/checkbox.tsx'
import { Field, FieldLabel } from '#/components/ui/field.tsx'
import { Input } from '#/components/ui/input.tsx'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '#/components/ui/select.tsx'
import type { DynamicFieldConfig } from '#/components/common/reserve/helper.ts'

interface DynamicFieldProps {
  field: DynamicFieldConfig
}

export default function DynamicField({ field }: DynamicFieldProps) {
  switch (field.kind) {
    case 'select':
      return (
        <Field orientation="responsive">
          <FieldLabel htmlFor={field.id} className="text-xl">
            {field.label}
          </FieldLabel>
          <Select value={field.value} onValueChange={field.onChange}>
            <SelectTrigger
              id={field.id}
              className="data-[size=default]:h-11 w-full border-primary border-2 bg-transparent text-lg hover:bg-transparent"
            >
              <SelectValue placeholder={field.placeholder} />
            </SelectTrigger>
            <SelectContent
              position="popper"
              align="start"
              sideOffset={4}
              className="border-primary border-2 bg-[url(/images/general/bg_pattern.webp]! bg-repeat"
            >
              {field.options.map((option) => (
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

    case 'number':
      return (
        <Field orientation="responsive">
          <FieldLabel htmlFor={field.id} className="text-xl">
            {field.label}
          </FieldLabel>
          <div className="relative w-16">
            <Input
              id={field.id}
              type="number"
              min={field.min}
              max={field.max}
              value={field.value}
              onChange={(e) =>
                field.onChange(Number(e.target.value) || field.min)
              }
              className="h-11 w-full pr-7 text-lg! text-white [-moz-appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
            />
            <div className="absolute inset-y-0 right-0 flex w-6 flex-col border-l-2 border-primary">
              <button
                type="button"
                aria-label="Increase"
                onClick={() =>
                  field.onChange(Math.min(field.max, field.value + 1))
                }
                disabled={field.value >= field.max}
                className="flex flex-1 items-center justify-center border-b border-primary bg-lagoon text-primary transition-colors hover:bg-primary hover:text-primary-foreground disabled:pointer-events-none disabled:opacity-50"
              >
                <ChevronUpIcon className="size-4" />
              </button>
              <button
                type="button"
                aria-label="Decrease"
                onClick={() =>
                  field.onChange(Math.max(field.min, field.value - 1))
                }
                disabled={field.value <= field.min}
                className="flex flex-1 items-center justify-center bg-lagoon text-primary transition-colors hover:bg-primary hover:text-primary-foreground disabled:pointer-events-none disabled:opacity-50"
              >
                <ChevronDownIcon className="size-4" />
              </button>
            </div>
          </div>
        </Field>
      )

    case 'checkbox':
      return (
        <Field orientation="horizontal" className="my-6 flex p-4 items-center">
          <Checkbox
            id={field.id}
            checked={field.checked}
            onCheckedChange={(checked) => field.onChange(checked === true)}
          />
          <FieldLabel htmlFor={field.id} className="text-xl font-normal">
            {field.label}
          </FieldLabel>
        </Field>
      )

    case 'text':
      return (
        <Field>
          <FieldLabel htmlFor={field.id} className="text-xl">
            {field.label}
          </FieldLabel>
          <Input
            id={field.id}
            name={field.name ?? field.id}
            type={field.type ?? 'text'}
            required={field.required}
            className="h-11 text-lg"
          />
        </Field>
      )

    case 'button-group':
      return (
        <div className="flex flex-col justify-evenly gap-4 md:flex-row">
          {field.options.map((option) => (
            <div key={option.value} className="my-2 mx-auto w-4/5 md:w-auto">
              <Button
                type="submit"
                name={field.name}
                value={option.value}
                className="w-full"
              >
                {option.label}
              </Button>
            </div>
          ))}
        </div>
      )
  }
}
