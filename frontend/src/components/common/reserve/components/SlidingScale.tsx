import { Slider } from '#/components/ui/slider.tsx'
import type { Show } from '#/interfaces/show'

interface SlidingScaleProps {
  show: Show
  customPrice: number
  setCustomPrice: (price: number) => void
}

export default function SlidingScale({
  show,
  customPrice,
  setCustomPrice,
}: SlidingScaleProps) {
  if (!show.baseTicketPrice) return null

  const minPrice = show.minTicketPrice ?? show.baseTicketPrice - 10
  const maxPrice = show.maxTicketPrice ?? show.baseTicketPrice + 10

  return (
    <div className="my-4 sm:my-6">
      <h4 className="mb-2 sm:mb-3 text-xl sm:text-2xl text-primary">Choose Your Price</h4>
      <p className="my-4 sm:my-6 text-base sm:text-lg">
        We offer sliding scale pricing to make our shows accessible. Pay what
        feels right for you! Your generosity directly supports the artists and
        sustains our community.
      </p>
      <div className="mb-3 sm:mb-4 flex items-center justify-center gap-2 sm:gap-3">
        <span className="text-lg sm:text-xl font-bold text-primary">
          Price per Ticket:
        </span>
        <span className="text-lg sm:text-xl font-bold text-primary min-w-[80px] sm:min-w-[100px] text-right">
          {customPrice} EUR
        </span>
      </div>
      <Slider
        value={[customPrice]}
        onValueChange={([value]) => setCustomPrice(value)}
        min={minPrice}
        max={maxPrice}
        step={1}
      />
      <div className="mt-2 flex justify-between text-xs sm:text-sm">
        <span>Soli price: {minPrice} EUR</span>
        <span>Standard: {show.baseTicketPrice} EUR</span>
        <span>Support price: {maxPrice} EUR</span>
      </div>
    </div>
  )
}
