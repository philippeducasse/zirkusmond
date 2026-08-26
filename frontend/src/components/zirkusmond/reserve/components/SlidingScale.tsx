import { Slider } from '#/components/ui/slider.tsx'
import type { Show } from '#/interfaces/show'
import { useTranslation } from 'react-i18next'

interface PriceLabelProps {
  label: string
  price: number
  alignment: 'start' | 'center' | 'end'
}

function PriceLabel({ label, price, alignment }: PriceLabelProps) {
  const alignmentClasses = {
    start: 'items-start',
    center: 'items-center',
    end: 'items-end',
  }

  return (
    <div className={`flex flex-col ${alignmentClasses[alignment]}`}>
      <span className="text-primary uppercase tracking-wider">{label}</span>
      <span className="text-white font-bold">{price} EUR</span>
    </div>
  )
}

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
  const { t } = useTranslation()

  if (!show.baseTicketPrice) return null

  const minPrice = show.minTicketPrice ?? show.baseTicketPrice - 10
  const maxPrice = show.maxTicketPrice ?? show.baseTicketPrice + 10

  return (
    <div className="my-4 sm:my-6">
      <h4 className="mb-2 sm:mb-3 text-primary text-center">
        {t('sliding_scale_title')}
      </h4>
      <p className="my-4 sm:my-6">{t('sliding_scale_description')}</p>
      <div className="mb-6 sm:mb-8 flex items-center justify-center gap-3 sm:gap-4 p-4 sm:p-5">
        <span className="text-lg sm:text-xl md:text-2xl font-semibold text-white/80">
          {t('sliding_scale_price_per_ticket')}
        </span>
        <span className="text-xl md:text-3xl font-bold text-primary">
          {customPrice}
        </span>
        <span className="text-xl md:text-3xll text-primary">€</span>
      </div>
      <Slider
        value={[customPrice]}
        onValueChange={([value]) => setCustomPrice(value)}
        min={minPrice}
        max={maxPrice}
        step={1}
      />
      <div className="mt-4 sm:mt-5 flex justify-between text-xs sm:text-sm md:text-base text-white/80 font-medium px-2 sm:px-4">
        <PriceLabel
          label={t('sliding_scale_solidarity')}
          price={minPrice}
          alignment="start"
        />
        <PriceLabel
          label={t('sliding_scale_standard')}
          price={show.baseTicketPrice}
          alignment="center"
        />
        <PriceLabel
          label={t('sliding_scale_support')}
          price={maxPrice}
          alignment="end"
        />
      </div>
    </div>
  )
}
