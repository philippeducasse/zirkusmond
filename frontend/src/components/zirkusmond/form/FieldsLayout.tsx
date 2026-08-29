interface FieldsLayoutProps {
  children: React.ReactNode;
}

export default function FieldsLayout({ children }: FieldsLayoutProps) {
  return <div className="flex justify-center flex-wrap gap-4">{children}</div>;
}
