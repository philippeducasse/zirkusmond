import { Field, FieldError, FieldLabel } from "#/components/ui/field.tsx";
import { Input } from "#/components/ui/input.tsx";

export interface TextFieldProps {
  id: string;
  label: string;
  name?: string;
  type?: string;
  required?: boolean;
  error?: string;
  onChange?: () => void;
}

export default function TextField({
  id,
  label,
  name,
  type = "text",
  required = false,
  error,
  onChange,
}: TextFieldProps) {
  return (
    <Field>
      <FieldLabel htmlFor={id} className="text-base sm:text-lg md:text-xl">
        {label}
      </FieldLabel>
      <Input
        id={id}
        name={name ?? id}
        type={type}
        required={required}
        aria-invalid={!!error}
        onChange={onChange}
        className="h-10 sm:h-11 text-base! sm:text-lg! text-white"
      />
      {error && <FieldError>{error}</FieldError>}
    </Field>
  );
}
