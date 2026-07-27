import { cn } from '#/lib/utils.ts'

function Skeleton({ className, ...props }: React.ComponentProps<'div'>) {
  return (
    <div
      data-slot="skeleton"
      className={cn('animate-shimmer rounded-none bg-[#6aadca]', className)}
      {...props}
    />
  )
}

export { Skeleton }
