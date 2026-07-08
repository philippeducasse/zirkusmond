import FormField from '#/components/common/reserve/FormField.tsx'

interface GuestFormProps {
  guestCount: number
}

export default function GuestForm({ guestCount }: GuestFormProps) {
  if (guestCount === 0) return null

  return (
    <div className="my-8 flex flex-col gap-6">
      {Array.from({ length: guestCount }, (_, i) => (
        <div key={i} className="border border-primary/40 p-8">
          <h4 className="mb-4 text-lg text-primary">Guest {i + 1}</h4>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 my-1">
            <FormField
              id={`guest-${i}-first-name`}
              label="First name"
              name={`guest-${i}-first-name`}
              required
            />
            <FormField
              id={`guest-${i}-last-name`}
              label="Last name"
              name={`guest-${i}-last-name`}
              required
            />
          </div>
        </div>
      ))}
    </div>
  )
}