import * as React from 'react'
import { cva } from 'class-variance-authority'
import type { VariantProps } from 'class-variance-authority'
import { Slot } from 'radix-ui'

import { cn } from '#/lib/utils.ts'

const buttonVariants = cva(
  "group/button inline-flex shrink-0 items-center justify-center rounded-none border border-transparent bg-clip-padding text-xs font-medium whitespace-nowrap transition-all outline-none select-none focus-visible:border-ring focus-visible:ring-1 focus-visible:ring-ring/50 active:not-aria-[haspopup]:translate-y-px disabled:pointer-events-none disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-1 aria-invalid:ring-destructive/20 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
  {
    variants: {
      variant: {
        primary:
          'font-bold text-primary bg-white/5 border-primary border-double tracking-wide duration-300 shadow-[0_10px_25px_-8px_rgba(0,0,0,0.5),0_0_18px_-6px_rgba(246,174,66,0.55)] hover:bg-black/10 hover:border-primary/80 hover:-translate-y-1 hover:shadow-[0_16px_32px_-10px_rgba(0,0,0,0.6),0_0_28px_-4px_rgba(246,174,66,0.8)] active:shadow-[0_4px_10px_-4px_rgba(0,0,0,0.4),0_0_10px_-4px_rgba(246,174,66,0.35)] disabled:opacity-80 disabled:cursor-not-allowed disabled:shadow-none disabled:translate-y-0',
        outline:
          'font-bold text-primary bg-white/5 tracking-wide duration-300 hover:bg-black/10 aria-expanded:bg-muted aria-expanded:text-foreground disabled:opacity-80 disabled:cursor-not-allowed disabled:shadow-none disabled:translate-y-0',
        secondary:
          'font-bold text-white bg-transparent border-primary border-double tracking-wide duration-300 shadow-[0_10px_25px_-8px_rgba(0,0,0,0.5),0_0_18px_-6px_color-mix(in_oklch,var(--secondary-foreground)_35%,transparent)] hover:bg-[color-mix(in_oklch,var(--secondary),var(--foreground)_5%)] hover:border-secondary-foreground/40 hover:-translate-y-1 hover:shadow-[0_16px_32px_-10px_rgba(0,0,0,0.6),0_0_28px_-4px_color-mix(in_oklch,var(--secondary-foreground)_45%,transparent)] active:shadow-[0_4px_10px_-4px_rgba(0,0,0,0.4),0_0_10px_-4px_color-mix(in_oklch,var(--secondary-foreground)_30%,transparent)] aria-expanded:bg-secondary aria-expanded:text-secondary-foreground disabled:opacity-80 disabled:cursor-not-allowed disabled:shadow-none disabled:translate-y-0',
        ghost:
          'font-bold text-primary tracking-wide duration-300 hover:text-primary/80 hover:-translate-y-1 active:translate-y-0 aria-expanded:text-primary/80 disabled:opacity-80 disabled:cursor-not-allowed disabled:translate-y-0',
        destructive:
          'font-bold text-destructive bg-destructive/10 border-destructive border-double tracking-wide duration-300 shadow-[0_10px_25px_-8px_rgba(0,0,0,0.5),0_0_18px_-6px_color-mix(in_oklch,var(--destructive)_45%,transparent)] hover:bg-destructive/20 hover:border-destructive/80 hover:-translate-y-1 hover:shadow-[0_16px_32px_-10px_rgba(0,0,0,0.6),0_0_28px_-4px_color-mix(in_oklch,var(--destructive)_60%,transparent)] focus-visible:border-destructive/40 focus-visible:ring-destructive/20 active:shadow-[0_4px_10px_-4px_rgba(0,0,0,0.4),0_0_10px_-4px_color-mix(in_oklch,var(--destructive)_35%,transparent)] disabled:opacity-80 disabled:cursor-not-allowed disabled:shadow-none disabled:translate-y-0',
        link: 'font-bold text-primary underline-offset-4 duration-300 hover:underline',
      },
      size: {
        default:
          'h-auto gap-1.5 text-2xl border-4 px-12 py-4 has-data-[icon=inline-end]:pr-8 has-data-[icon=inline-start]:pl-8',
        sm: "h-auto gap-1 text-base border-2 px-6 py-2.5 has-data-[icon=inline-end]:pr-4 has-data-[icon=inline-start]:pl-4 [&_svg:not([class*='size-'])]:size-4",
        xs: "h-auto gap-1 text-sm border-2 px-3 py-1.5 has-data-[icon=inline-end]:pr-2 has-data-[icon=inline-start]:pl-2 [&_svg:not([class*='size-'])]:size-3.5",
        icon: 'size-8',
        'icon-xs': "size-6 rounded-none [&_svg:not([class*='size-'])]:size-3",
        'icon-sm': 'size-7 rounded-none',
        'icon-lg': 'size-9',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'default',
    },
  },
)

function Button({
  className,
  variant = 'primary',
  size = 'default',
  asChild = false,
  ...props
}: React.ComponentProps<'button'> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean
  }) {
  const Comp = asChild ? Slot.Root : 'button'

  return (
    <Comp
      data-slot="button"
      data-variant={variant}
      data-size={size}
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants }
