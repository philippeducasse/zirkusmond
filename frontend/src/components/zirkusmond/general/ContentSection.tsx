import type { ReactNode } from 'react'
import { cn } from '#/lib/utils.ts'

interface ContentSectionProps {
  children: ReactNode
  className?: string
}

/**
 * Standardized content section component with island-shell styling.
 * Used for main content blocks with rounded corners and consistent padding.
 */
export default function ContentSection({
  children,
  className,
}: ContentSectionProps) {
  return (
    <section className={cn('island-shell rounded-2xl p-4 sm:p-6 md:p-10', className)}>
      {children}
    </section>
  )
}