import { Button } from '#/components/ui/button'
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/')({ component: App })

function App() {
  return (
    <div className="flex h-screen w-full">
      <Button className="m-auto">Tickets Kaufen</Button>
    </div>
  )
}
