import DynamicField from '#/components/common/form/DynamicField'
import FieldsLayout from '#/components/common/form/FieldsLayout'
import type { DynamicFieldConfig } from '#/components/common/reserve/helper.ts'

interface DynamicFormProps {
  fields: DynamicFieldConfig[]
  title?: string
}

export default function DynamicForm({ fields, title }: DynamicFormProps) {
  return (
    <FieldsLayout>
      {title && (
        <h3 className="text-3xl text-primary text-center w-full">{title}</h3>
      )}
      {fields.map((field) => (
        <DynamicField key={field.id} field={field} />
      ))}
    </FieldsLayout>
  )
}
