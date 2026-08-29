import { Button } from "#/components/ui/button.tsx";

export interface ButtonGroupFieldProps {
  name: string;
  options: { value: string; label: string }[];
}

export default function ButtonGroupField({
  name,
  options,
}: ButtonGroupFieldProps) {
  return (
    <div className="flex flex-col justify-evenly gap-4 md:flex-row">
      {options.map((option) => (
        <div key={option.value} className="my-2 mx-auto w-4/5 md:w-auto">
          <Button
            type="submit"
            name={name}
            value={option.value}
            className="w-full"
          >
            {option.label}
          </Button>
        </div>
      ))}
    </div>
  );
}
