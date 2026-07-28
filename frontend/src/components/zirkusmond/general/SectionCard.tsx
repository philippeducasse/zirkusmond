import { Card } from '#/components/ui/card'
import type { ReactNode } from 'react'
import { cn } from '#/lib/utils.ts'

interface SectionCardProps {
  children: ReactNode
  className?: string
}

const SectionCard = ({ children, className }: SectionCardProps) => {
  return (
    <Card
      className={cn(
        'text-white bg-black/10 border-5 border-primary border-double p-2 md:p-8',
        className,
      )}
    >
      {children}
    </Card>
  )
}

export default SectionCard
