import type { ReactNode } from "react";
import { cn } from "#/lib/utils.ts";

interface NavigationButtonWrapperProps {
  children: ReactNode;
  className?: string;
}

export default function NavigationButtonWrapper({
  children,
  className,
}: NavigationButtonWrapperProps) {
  return (
    <div
      className={cn(
        "flex flex-col sm:flex-row-reverse sm:justify-between gap-4 mt-8 text-center",
        className,
      )}
    >
      {children}
    </div>
  );
}
