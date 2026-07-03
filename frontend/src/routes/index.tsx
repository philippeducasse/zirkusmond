import { Button } from '#/components/ui/button'
import { Card } from '#/components/ui/card'
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/')({ component: App })

function App() {
  return (
    <>
      <h1>Index page</h1>
      <Button variant={'outline'} size={'lg'}>
        Button
      </Button>
      <Card></Card>
    </>
  )
}
