import { Link } from '@tanstack/react-router'

import PageContainer from '#/components/zirkusmond/general/PageContainer'
import PageHeader from '#/components/zirkusmond/general/PageHeader'
import ContentSection from '#/components/zirkusmond/general/ContentSection'
import SectionCard from '#/components/zirkusmond/general/SectionCard'
import { Button } from '#/components/ui/button.tsx'

interface NotFoundProps {
  entityName?: string
}

export default function NotFound({ entityName = 'Page' }: NotFoundProps) {
  return (
    <PageContainer className="flex flex-col items-center gap-6 px-4 text-center">
      <PageHeader>{entityName} not found</PageHeader>
      <ContentSection>
        <SectionCard>
          <p>
            This {entityName.toLowerCase()} doesn&apos;t exist or is no longer
            available.
          </p>
          <Button
            variant={'secondary'}
            asChild
            className=" w-full md:w-1/2 mx-auto mt-10"
          >
            <Link to="/">Home</Link>
          </Button>
        </SectionCard>
      </ContentSection>
    </PageContainer>
  )
}
