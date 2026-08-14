import { cn } from '#/lib/utils.ts'
import SectionCard from './SectionCard'
import { SERVER_API_URL } from '#/lib/api.ts'

interface TeamMember {
  image: string
  name: string
  role: string
}

interface TeamGridProps {
  members: TeamMember[]
  className?: string
}

export default function TeamGrid({ members, className }: TeamGridProps) {
  return (
    <div className={cn('flex flex-wrap justify-center gap-6', className)}>
      {members.map((member) => (
        <TeamMemberCard key={member.name} member={member} />
      ))}
    </div>
  )
}

interface TeamMemberCardProps {
  member: TeamMember
  className?: string
}

function TeamMemberCard({ member, className }: TeamMemberCardProps) {
  return (
    <SectionCard className="p-0!">
      <div className={cn('text-center mb-4', className)}>
        <img
          className="mx-auto aspect-square w-full  object-cover max-w-xs"
          src={`${SERVER_API_URL}${member.image}`}
          alt={`Photo of ${member.name}`}
        />
        <h3>{member.name}</h3>
        <p>{member.role}</p>
      </div>
    </SectionCard>
  )
}

export type { TeamMember }
