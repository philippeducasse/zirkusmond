import { useState } from 'react'
import { ChevronDown } from 'lucide-react'
import { useTranslation } from 'react-i18next'

import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from '#/components/ui/card.tsx'
import { Button } from '#/components/ui/button.tsx'
import { cn } from '#/lib/utils.ts'

interface EventCardProps {
  eventTitle: string
  eventImageUrl: string
  eventDates: string[]
}

const EventCard = ({
  eventTitle,
  eventImageUrl,
  eventDates,
}: EventCardProps) => {
  const { t } = useTranslation()
  const [expanded, setExpanded] = useState(false)
  const visibleDates = eventDates.slice(0, 3)
  const hiddenDates = eventDates.slice(3)

  return (
    <Card className="relative mx-auto h-full w-full min-w-70 max-w-112.5 cursor-pointer justify-between border-[5px] border-double border-[#e7b548] bg-black/5 pt-0 shadow-[0_10px_25px_-8px_rgba(0,0,0,0.5),0_0_18px_-6px_rgba(246,174,66,0.55)] transition-all duration-300 hover:-translate-y-1 hover:border-[#e7b548]/80 hover:bg-black/10 hover:shadow-[0_16px_32px_-10px_rgba(0,0,0,0.6),0_0_28px_-4px_rgba(246,174,66,0.8)]">
      <img
        src={eventImageUrl}
        alt="Event cover"
        className="relative z-20 aspect-square w-full object-cover"
      />
      <CardHeader className="py-3 my-auto">
        <CardTitle className="text-center pb-2 text-primary text-lg sm:text-xl md:text-2xl">
          {eventTitle}
        </CardTitle>
        {visibleDates.map((date, i) => (
          <CardDescription
            key={`${date}_${i}`}
            className="w-full text-center text-sm sm:text-base md:text-lg text-white"
          >
            {date}
          </CardDescription>
        ))}
        {hiddenDates.length > 0 && (
          <>
            <div
              className={cn(
                'grid transition-[grid-template-rows] duration-300 ease-in-out',
                expanded ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]',
              )}
            >
              <div className="overflow-hidden">
                {hiddenDates.map((date, i) => (
                  <CardDescription
                    key={`${date}_${i}`}
                    className="w-full text-center text-sm sm:text-base md:text-lg text-white"
                  >
                    {date}
                  </CardDescription>
                ))}
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              aria-expanded={expanded}
              className="mx-auto gap-1"
              onClick={(e) => {
                e.preventDefault()
                e.stopPropagation()
                setExpanded((prev) => !prev)
              }}
            >
              {expanded ? t('event_card_show_less') : t('event_card_show_all_dates')}
              <ChevronDown
                className={cn(
                  'transition-transform duration-300',
                  expanded && 'rotate-180',
                )}
              />
            </Button>
          </>
        )}
      </CardHeader>
    </Card>
  )
}

export default EventCard
