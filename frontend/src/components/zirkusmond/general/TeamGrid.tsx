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
        'grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-5',
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
    <SectionCard>
      <div className={cn('text-center', className)}>
        <img
          className="mx-auto aspect-square w-full rounded-xl object-cover"
          src={member.image}
          alt={`Photo of ${member.name}`}
        />
        <h3 className="display-title mt-4 sm:mt-6 font-bold text-(--sea-ink)">
          {member.name}
        </h3>
        <p className="mt-1 text-(--sea-ink-soft)">{member.role}</p>
      </div>
    </SectionCard>
  )
}

export type { TeamMember }