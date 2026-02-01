import { createFileRoute } from '@tanstack/react-router'

import { $api } from '@/lib/api'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { ArrowLeftIcon, ImageIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

function RouteComponent() {
  const id = Route.useParams().id
  const url = $api.useQuery(
    'get',
    '/api/v1/scan/{id}',
    {
      params: { path: { id } },
    },
    { refetchInterval: 500 },
  )

  const [fitScreen, setFitScreen] = useState(false)

  if (!url.data) {
    return <div>{JSON.stringify(url.data)}</div>
  }

  return (
    <>
      <h2 className="font-display text-xl text-purple-900">{url.data.title}</h2>
      Submitted URL
      <h1 className="font-semibold text-purple-950">{url.data.original_url}</h1>
      Destination URL
      <h2 className="font-semibold text-purple-950">{url.data.final_url}</h2>
      <img
        src={url.data ? `data:image/png;bas e64,${url.data.screenshot}` : ''}
        alt="Screenshot"
        className={cn(
          'object-cover object-top  border bg-background shadow transition-all',
          fitScreen
            ? 'w-full h-full cursor-zoom-out rounded-2xl'
            : 'w-96 h-96 cursor-zoom-in rounded',
        )}
        onClick={() => setFitScreen((prev) => !prev)}
      />
    </>
  )
}

export const Route = createFileRoute('/$id')({
  component: RouteComponent,
})
