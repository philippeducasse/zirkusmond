import { Link } from "@tanstack/react-router";
import { useTranslation } from "react-i18next";

import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
} from "#/components/ui/navigation-menu.tsx";
import LocaleSwitcher from "./LocaleSwitcher.tsx";

import type { NavItem } from "./nav-items.ts";

interface DesktopNavProps {
  items: NavItem[];
}

const linkClassName =
  "w-fit rounded-none text-primary bg-transparent p-0 text-xl md:text-2xl hover:bg-transparent focus:bg-transparent";

export default function DesktopNav({ items }: DesktopNavProps) {
  const { t } = useTranslation();

  return (
    <div className="hidden items-center gap-6 md:flex">
      <NavigationMenu viewport={false} className="max-w-none">
        <NavigationMenuList className="gap-5">
          {items.map((item) => (
            <NavigationMenuItem key={item.href}>
              <NavigationMenuLink asChild className={linkClassName}>
                {item.external ? (
                  <a href={item.href}>{t(item.labelKey)}</a>
                ) : (
                  <Link to={item.href}>{t(item.labelKey)}</Link>
                )}
              </NavigationMenuLink>
            </NavigationMenuItem>
          ))}
        </NavigationMenuList>
      </NavigationMenu>
      <LocaleSwitcher />
    </div>
  );
}
