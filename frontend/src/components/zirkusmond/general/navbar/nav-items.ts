export interface NavItem {
  labelKey: string;
  href: string;
  /** Renders as a plain anchor instead of a router Link, for pages outside this app (e.g. the Django-served QR scanner). */
  external?: boolean;
}

export const NAV_ITEMS: NavItem[] = [
  { labelKey: "nav_events", href: "/events" },
  { labelKey: "nav_about", href: "/about" },
  { labelKey: "nav_contact", href: "/contact" },
];
