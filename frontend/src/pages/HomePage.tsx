import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

export function HomePage() {
  return (
    <div className="space-y-8">
      <div className="space-y-3">
        <h1 className="text-4xl font-bold tracking-tight">
          Catastrophe Exposure Aggregator
        </h1>
        <p className="text-lg text-muted-foreground">
          Aggregate and analyse catastrophe exposure data across portfolios.
        </p>
      </div>

      <div className="grid gap-6 sm:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>System Health</CardTitle>
            <CardDescription>
              Monitor backend services, Redis cache, and API connectivity.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link to="/health">
              <Button variant="outline" className="w-full">
                View Health Status
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Exposure Data</CardTitle>
            <CardDescription>
              Upload, aggregate, and query catastrophe exposure data.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" className="w-full" disabled>
              Coming Soon
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
