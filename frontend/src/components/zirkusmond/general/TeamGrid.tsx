import { cn } from "#/lib/utils.ts";
import SectionCard from "./SectionCard";

interface TeamMember {
  image: string;
  name: string;
  role: string;
}

interface TeamGridProps {
  members: TeamMember[];
  className?: string;
}

const TeamGrid = ({ members, className }: TeamGridProps) => {
  return (
    <div className={cn("flex flex-wrap justify-center gap-6", className)}>
      {members.map((member) => (
        <TeamMemberCard key={member.name} member={member} />
      ))}
    </div>
  );
};

interface TeamMemberCardProps {
  member: TeamMember;
  className?: string;
}

const TeamMemberCard = ({ member, className }: TeamMemberCardProps) => {
  return (
    <SectionCard className="p-0! min-w-60">
      <div className={cn("text-center mb-4", className)}>
        <img
          className="mx-auto aspect-square w-full object-cover object-top max-w-md"
          src={member.image}
          alt={`Photo of ${member.name}`}
        />
        <h3>{member.name}</h3>
        <p>{member.role}</p>
      </div>
    </SectionCard>
  );
};

export default TeamGrid;
export type { TeamMember };
