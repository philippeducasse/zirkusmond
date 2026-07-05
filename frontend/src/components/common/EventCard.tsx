import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

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
  return (
    <Card className="relative mx-auto h-fit min-h-[600px] w-[450px] cursor-pointer justify-between border-[5px] border-double border-[#e7b548] bg-white/5 pt-0 shadow-[0_10px_25px_-8px_rgba(0,0,0,0.5),0_0_18px_-6px_rgba(246,174,66,0.55)] transition-all duration-300 hover:-translate-y-1 hover:border-[#e7b548]/80 hover:bg-black/10 hover:shadow-[0_16px_32px_-10px_rgba(0,0,0,0.6),0_0_28px_-4px_rgba(246,174,66,0.8)]">
      <img
        src={eventImageUrl}
        alt="Event cover"
        className="relative z-20 h-[450px] w-[450px] object-cover"
      />
      <CardHeader className="py-3">
        <CardTitle className="text-center pb-2 text-primary text-xl md:text-2xl">
          {eventTitle}
        </CardTitle>
        {eventDates.map((date) => (
          <CardDescription className="w-full text-center text-lg text-white lg:p-2">
            {date}
          </CardDescription>
        ))}
      </CardHeader>
    </Card>
  )
}

export default EventCard
