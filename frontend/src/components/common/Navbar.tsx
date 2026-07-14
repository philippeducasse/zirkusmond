import { cn } from '#/lib/utils.ts'
import { useNavbar } from '#/hooks/useNavbar.ts'

import Logo from './navbar/Logo.tsx'
import DesktopNav from './navbar/DesktopNav.tsx'
import MobileNav from './navbar/MobileNav.tsx'
import { NAV_ITEMS, QR_SCANNER_ITEM } from './navbar/nav-items.ts'

interface NavbarProps {
  isStaff?: boolean
}

export default function Navbar({ isStaff = false }: NavbarProps) {
  const { fixed, sentinelRef, scrollThreshold } = useNavbar()
  const items = isStaff ? [...NAV_ITEMS, QR_SCANNER_ITEM] : NAV_ITEMS
  console.log({ fixed })
  return (
    <>
      <div
        ref={sentinelRef}
        aria-hidden
        className="pointer-events-none absolute top-0 left-0 w-px"
        style={{ height: scrollThreshold }}
      />
      <header
        className={cn(
          'fixed inset-x-0 top-0 z-50 flex h-20 items-center justify-between border-b-[3px] border-primary px-6 backface-hidden transition-all delay-200 duration-[600ms] md:px-12 lg:px-24',
          fixed
            ? 'visible bg-[url(/images/general/bg_pattern.webp)] opacity-100'
            : 'invisible opacity-0',
        )}
      >
        <Logo />
        <DesktopNav items={items} />
        <MobileNav items={items} />
      </header>
    </>
  )
}
