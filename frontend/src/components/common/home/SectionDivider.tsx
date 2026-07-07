import { cn } from '#/lib/utils.ts'

type SectionDividerType = 'kite' | 'flower' | 'moon'

const DIVIDER_IMAGES: Record<SectionDividerType, string> = {
  kite: '/images/general/kite_sepator.webp',
  flower: '/images/general/flower_separator.webp',
  moon: '/images/general/moon_separator.webp',
}

interface SectionDividerProps {
  type: SectionDividerType
  className?: string
}

export default function SectionDivider({
  type,
  className,
}: SectionDividerProps) {
  return (
    <img
      src={DIVIDER_IMAGES[type]}
      alt={'Verzierung'}
      className={cn(
        'mx-auto my-16 w-[70%] max-w-[1200px] max-md:w-full',
        className,
      )}
    />
  )
}
