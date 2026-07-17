import { Card } from '#/components/ui/card'
import type { ReactNode } from 'react'

interface SectionCardProps {
  children: ReactNode
}

const SectionCard = ({ children }: SectionCardProps) => {
  return (
    <Card className="text-white bg-black/10 border-5 border-primary border-double p-2 md:p-8">
      {children}
    </Card>
  )
}

export default SectionCard
