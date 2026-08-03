import ButtonGroupField from '#/components/zirkusmond/form/ButtonGroupField'
import CheckboxField from '#/components/zirkusmond/form/CheckboxField'
import NumberField from '#/components/zirkusmond/form/NumberField'
import SelectField from '#/components/zirkusmond/form/SelectField'
import TextField from '#/components/zirkusmond/form/TextField'
import {
  FieldType,
  type DynamicFieldConfig,
} from '#/components/zirkusmond/reserve/buildFormFields'

interface DynamicFieldProps {
  field: DynamicFieldConfig
}

export default function DynamicField({ field }: DynamicFieldProps) {
  switch (field.fieldType) {
    case FieldType.Select:
      return <SelectField {...field} />

    case FieldType.Number:
      return <NumberField {...field} />

    case FieldType.Checkbox:
      return <CheckboxField {...field} />

    case FieldType.Text:
      return <TextField {...field} />

    case FieldType.ButtonGroup:
      return <ButtonGroupField {...field} />
  }
}
