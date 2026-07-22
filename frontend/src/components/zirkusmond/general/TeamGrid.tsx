import type { ReactNode } from 'react'
import { cn } from '#/lib/utils.ts'
import SectionCard from './SectionCard'

interface TeamMember {
  image: string
  name: string
  role: string
}

interface TeamGridProps {
  members: TeamMember[]
  className?: string
}

/**
 * Standardized team member grid component.
 * Displays team members in a responsive grid with photos, names, and roles.
 */
export default function TeamGrid({ members, className }: TeamGridProps) {
  return (
    <div
      className={cn(
        'grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3',
        className,
      )}
    >
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
          className="mx-auto aspect-square w-full  object-cover"
          src={member.image}
          alt={`Photo of ${member.name}`}
        />
        <h3>{member.name}</h3>
        <p>{member.role}</p>
      </div>
    </SectionCard>
  )
}

export type { TeamMember }
