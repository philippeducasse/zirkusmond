import { Card, CardContent, CardDescription } from '#/components/ui/card.tsx'

interface TimeDetailsProps {
  date: string
  beginTime: string
  admissionTime: string
}

export default function TimeDetails({
  date,
  beginTime,
  admissionTime,
}: TimeDetailsProps) {
  return (
    <Card className="max-w-62.5 border-2 border-primary bg-transparent text-left">
      <CardContent className="px-6 sm:px-8 py-3 sm:py-4">
        <CardDescription className="mb-2 font-bold text-center text-base sm:text-lg text-white">
          {date}
        </CardDescription>
        <p className="text-primary font-semibold text-sm sm:text-base">Show begin: {beginTime}</p>
        <p className="text-primary font-semibold text-sm sm:text-base">Admission: {admissionTime}</p>
      </CardContent>
    </Card>
  )
}
