import { Drama, Info, Mail } from "lucide-react";
import type { LucideIcon } from "lucide-react";

export interface NavItem {
  labelKey: string;
  href: string;
  icon: LucideIcon;
  /** Renders as a plain anchor instead of a router Link, for pages outside this app (e.g. the Django-served QR scanner). */
  external?: boolean;
}

export const NAV_ITEMS: NavItem[] = [
  { labelKey: "nav_events", href: "/shows", icon: Drama },
  { labelKey: "nav_about", href: "/about", icon: Info },
  { labelKey: "nav_contact", href: "/contact", icon: Mail },
];
