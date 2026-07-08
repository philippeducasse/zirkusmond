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
    <Card className="max-w-[250px] border-2 border-primary bg-transparent text-left">
      <CardContent className="px-8 py-4">
        <CardDescription className="mb-2 font-bold text-center text-lg text-white">
          {date}
        </CardDescription>
        <p className="text-primary">Show begin: {beginTime}</p>
        <p className="text-primary">Admission: {admissionTime}</p>
      </CardContent>
    </Card>
  )
}
