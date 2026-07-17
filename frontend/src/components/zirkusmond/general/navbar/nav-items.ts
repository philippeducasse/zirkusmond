export interface NavItem {
  label: string
  href: string
  /** Renders as a plain anchor instead of a router Link, for pages outside this app (e.g. the Django-served QR scanner). */
  external?: boolean
}

export const NAV_ITEMS: NavItem[] = [
  { label: 'Events', href: '/events' },
  { label: 'About', href: '/about' },
  { label: 'Contact', href: '/contact' },
]

export const QR_SCANNER_ITEM: NavItem = {
  label: 'QR Scanner',
  href: '/qr-scanner/',
  external: true,
}