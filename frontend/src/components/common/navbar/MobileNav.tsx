import { Menu } from 'lucide-react'
import { Link } from '@tanstack/react-router'

import { Button } from '#/components/ui/button.tsx'
import { Separator } from '#/components/ui/separator.tsx'
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '#/components/ui/sheet.tsx'
import LocaleSwitcher from './LocaleSwitcher.tsx'

import type { NavItem } from './nav-items.ts'

interface MobileNavProps {
  items: NavItem[]
}

export default function MobileNav({ items }: MobileNavProps) {
  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          aria-label="Toggle menu"
          className="md:hidden"
        >
          <Menu className="size-6" />
        </Button>
      </SheetTrigger>
      <SheetContent side="right" className="border-l-2 border-[#e7b548]">
        <SheetHeader>
          <SheetTitle>Menu</SheetTitle>
        </SheetHeader>
        <nav className="flex flex-col items-center gap-4 p-4">
          {items.map((item) =>
            item.external ? (
              <SheetClose key={item.href} asChild>
                <a href={item.href} className="text-2xl">
                  {item.label}
                </a>
              </SheetClose>
            ) : (
              <SheetClose key={item.href} asChild>
                <Link to={item.href} className="text-2xl">
                  {item.label}
                </Link>
              </SheetClose>
            ),
          )}
        </nav>
        <Separator />
        <div className="flex justify-center p-4">
          <LocaleSwitcher />
        </div>
      </SheetContent>
    </Sheet>
  )
}
