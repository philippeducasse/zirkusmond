import ButtonGroupField from '#/components/zirkusmond/form/ButtonGroupField'
import CheckboxField from '#/components/zirkusmond/form/CheckboxField'
import NumberField from '#/components/zirkusmond/form/NumberField'
import SelectField from '#/components/zirkusmond/form/SelectField'
import TextField from '#/components/zirkusmond/form/TextField'
import type { DynamicFieldConfig } from '#/components/zirkusmond/reserve/helper'

interface DynamicFieldProps {
  field: DynamicFieldConfig
}

export default function DynamicField({ field }: DynamicFieldProps) {
  switch (field.kind) {
    case 'select':
      return <SelectField {...field} />

    case 'number':
      return <NumberField {...field} />

    case 'checkbox':
      return <CheckboxField {...field} />

    case 'text':
      return <TextField {...field} />

    case 'button-group':
      return <ButtonGroupField {...field} />
  }
}
