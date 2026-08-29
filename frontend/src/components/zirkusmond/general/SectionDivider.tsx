import { cn } from "#/lib/utils.ts";

type SectionDividerType = "kite" | "flower" | "moon";
type SectionDividerMargin = "default" | "small";

const DIVIDER_IMAGES: Record<SectionDividerType, string> = {
  kite: "/images/general/kite_sepator.webp",
  flower: "/images/general/flower_separator.webp",
  moon: "/images/general/moon_separator.webp",
};

const DIVIDER_MARGINS: Record<SectionDividerMargin, string> = {
  default: "my-16",
  small: "my-4",
};

interface SectionDividerProps {
  type: SectionDividerType;
  margin?: SectionDividerMargin;
  className?: string;
}

export default function SectionDivider({
  type,
  margin = "default",
  className,
}: SectionDividerProps) {
  return (
    <img
      src={DIVIDER_IMAGES[type]}
      alt={"Verzierung"}
      className={cn(
        "mx-auto w-[70%] max-w-[1200px] max-md:w-full",
        DIVIDER_MARGINS[margin],
        className,
      )}
    />
  );
}
