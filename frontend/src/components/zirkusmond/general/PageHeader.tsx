import type { ReactNode } from "react";
import { cn } from "#/lib/utils.ts";

interface PageHeaderProps {
  children: ReactNode;
  className?: string;
}

/**
 * Standardized page header component for displaying titles consistently across pages.
 * Uses display-title class for responsive sizing.
 */
export default function PageHeader({ children, className }: PageHeaderProps) {
  return (
    <h2 className={cn("display-title mb-6 sm:mb-16 text-center", className)}>
      {children}
    </h2>
  );
}
