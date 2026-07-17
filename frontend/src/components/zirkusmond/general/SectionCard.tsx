import { Card } from '#/components/ui/card'
import type { ReactNode } from 'react'

interface SectionCardProps {
  children: ReactNode
}

const SectionCard = ({ children }: SectionCardProps) => {
  return <Card>{children}</Card>
}

export default SectionCard
