import { createFileRoute } from '@tanstack/react-router'
import ContactSection from '#/components/zirkusmond/home/ContactSection'

export const Route = createFileRoute('/contact')({
  head: () => ({
    meta: [{ title: 'Zirkus Mond – Kontakt' }],
  }),
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <div className="flex items-center justify-center py-12">
      <ContactSection />
    </div>
  )
}
