import type { ReactNode } from 'react'

import { cn } from '#/lib/utils.ts'

interface PageContainerProps {
  children: ReactNode
  className?: string
}

/**
 * Shared content wrapper for every route except the homepage.
 * The navbar is fixed and opaque on all non-home pages (see useNavbar.ts),
 * so pt-28 keeps content clear of it; page-wrap caps the reading width and
 * centers it responsively.
 */
export default function PageContainer({
  children,
  className,
}: PageContainerProps) {
  return (
    <main className={cn('page-wrap pt-28 pb-16', className)}>{children}</main>
  )
}
