import i18n from '#/i18n'

export interface NavItem {
  label: string
  href: string
  /** Renders as a plain anchor instead of a router Link, for pages outside this app (e.g. the Django-served QR scanner). */
  external?: boolean
}

export const NAV_ITEMS: NavItem[] = [
  { label: i18n.t('nav_events'), href: '/events' },
  { label: i18n.t('nav_about'), href: '/about' },
  { label: i18n.t('nav_contact'), href: '/contact' },
]