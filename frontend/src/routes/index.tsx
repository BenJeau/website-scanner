import { createFileRoute, useNavigate } from '@tanstack/react-router'

import { $api } from '@/lib/api'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

function App() {
  const scanUrl = $api.useMutation('post', '/api/v1/scan')
  const navigate = useNavigate()

  return (
    <form
      onSubmit={async (e) => {
        e.preventDefault()
        const url = e.target.url.value
        const data = await scanUrl.mutateAsync({
          params: {
            query: {
              url,
            },
          },
        })

        navigate({
          to: '/$id',
          params: {
            id: data.id,
          },
        })
      }}
    >
      <Input type="url" name="url" />
      <Button type="submit">Scan</Button>
    </form>
  )
}

export const Route = createFileRoute('/')({
  component: App,
})
