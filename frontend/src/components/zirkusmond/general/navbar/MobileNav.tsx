import { Menu, XIcon } from 'lucide-react'
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
import Logo from './Logo.tsx'

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
          <Menu className="size-8" />
        </Button>
      </SheetTrigger>
      <SheetContent
        showCloseButton={false}
        className="border-l-2 border-primary bg-[url(/images/general/bg_pattern.webp)] bg-repeat w-full"
      >
        <SheetHeader className="flex flex-row justify-between">
          <SheetTitle className="text-primary text-2xl max-w-1/2">
            Menu
          </SheetTitle>
          <SheetClose className="max-w-8">
            <XIcon className="text-primary" />
          </SheetClose>
        </SheetHeader>
        <nav className="flex flex-col items-center gap-4 p-4">
          {items.map((item) =>
            item.external ? (
              <SheetClose key={item.href} asChild>
                <a
                  href={item.href}
                  className="text-xl sm:text-2xl text-primary"
                >
                  {item.label}
                </a>
              </SheetClose>
            ) : (
              <SheetClose key={item.href} asChild>
                <Link
                  to={item.href}
                  className="text-xl sm:text-2xl text-primary"
                >
                  {item.label}
                </Link>
              </SheetClose>
            ),
          )}
        </nav>
        <div className="my-6">
          <Separator className="bg-primary mb-0.5" />
          <Separator className="bg-primary" />
        </div>
        <div className="flex flex-col gap-12 align-middle justify-center p-4 mx-auto">
          <LocaleSwitcher />
          <Logo />
        </div>
      </SheetContent>
    </Sheet>
  )
}
