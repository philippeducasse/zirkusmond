import type { ReactNode } from 'react'
import { cn } from '#/lib/utils.ts'
import CrossFade from './CrossFade.tsx'

interface ContentSectionProps {
  children: ReactNode
  className?: string
  isLoading?: boolean
  skeleton?: ReactNode
  duration?: number
}

/**
 * Standardized content section component with island-shell styling.
 * Used for main content blocks with rounded corners and consistent padding.
 * Optionally supports crossfade transitions from skeleton to content.
 */
export default function ContentSection({
  children,
  className,
  isLoading,
  skeleton,
  duration,
}: ContentSectionProps) {
  return (
    <section className={cn('island-shell rounded-2xl p-2 md:p-10', className)}>
      {isLoading !== undefined && skeleton ? (
        <CrossFade
          isLoading={isLoading}
          skeleton={skeleton}
          duration={duration}
        >
          {children}
        </CrossFade>
      ) : (
        children
      )}
    </section>
  )
}
