import { Checkbox } from "#/components/ui/checkbox.tsx";
import { Field, FieldLabel } from "#/components/ui/field.tsx";

export interface CheckboxFieldProps {
  id: string;
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}

export default function CheckboxField({
  id,
  label,
  checked,
  onChange,
}: CheckboxFieldProps) {
  return (
    <Field
      orientation="horizontal"
      className="flex items-center max-w-62 sm:max-w-md md:max-w-lg"
    >
      <FieldLabel
        htmlFor={id}
        className="text-base sm:text-lg md:text-xl w-min flex-none"
      >
        {label}
      </FieldLabel>
      <Checkbox
        id={id}
        checked={checked}
        onCheckedChange={(check) => onChange(check === true)}
      />
    </Field>
  );
}
