import { Card, CardContent, CardDescription } from '#/components/ui/card.tsx'
import { useTranslation } from 'react-i18next'

interface TimeDetailsProps {
  date: string
  admissionTime: string
}

export default function TimeDetails({ date, admissionTime }: TimeDetailsProps) {
  const { t } = useTranslation()
  return (
    <Card className="max-w-62.5 border-2 border-primary bg-transparent text-left">
      <CardContent className="px-6 sm:px-8 py-3 sm:py-4">
        <CardDescription className="mb-2 font-bold text-center text-base sm:text-lg text-primary">
          {date}
        </CardDescription>
        <p className="font-semibold">
          {t('show_admission')} {admissionTime}
        </p>
      </CardContent>
    </Card>
  )
}
