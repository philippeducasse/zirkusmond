import ButtonGroupField from '#/components/common/form/ButtonGroupField.tsx'
import CheckboxField from '#/components/common/form/CheckboxField.tsx'
import NumberField from '#/components/common/form/NumberField.tsx'
import SelectField from '#/components/common/form/SelectField.tsx'
import TextField from '#/components/common/form/TextField.tsx'
import type { DynamicFieldConfig } from '#/components/common/reserve/helper.ts'

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
