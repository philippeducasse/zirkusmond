import DynamicField from '#/components/zirkusmond/form/DynamicField'
import FieldsLayout from '#/components/zirkusmond/form/FieldsLayout'
import type { DynamicFieldConfig } from '#/components/zirkusmond/reserve/formFieldBuilders'

interface DynamicFormProps {
  fields: DynamicFieldConfig[]
  title?: string
}

export default function DynamicForm({ fields, title }: DynamicFormProps) {
  return (
    <FieldsLayout>
      {title && <h3 className="text-primary text-center w-full">{title}</h3>}
      {fields.map((field) => (
        <DynamicField key={field.id} field={field} />
      ))}
    </FieldsLayout>
  )
}
