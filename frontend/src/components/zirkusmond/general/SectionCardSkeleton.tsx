import SectionCard from "./SectionCard";
import { Skeleton } from "#/components/ui/skeleton";
import { cn } from "#/lib/utils.ts";

interface SectionCardSkeletonProps {
  className?: string;
  lines?: number;
}

const SectionCardSkeleton = ({
  className,
  lines = 3,
}: SectionCardSkeletonProps) => {
  return (
    <SectionCard className={cn("space-y-4 ", className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          className="h-6 w-full min-w-[300px] rounded-full"
          style={{
            animationDelay: `${i * 0.15}s`,
            animationFillMode: "backwards",
          }}
        />
      ))}
    </SectionCard>
  );
};

export default SectionCardSkeleton;
