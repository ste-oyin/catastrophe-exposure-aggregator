import { useEffect, useState } from 'react'
import { Badge } from '@/components/ui/badge'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'

interface HealthResponse {
  status: string
  version: string
  redis: string
}

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api'

export function HealthPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchHealth = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/health`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data: HealthResponse = await res.json()
      setHealth(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reach backend')
      setHealth(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHealth()
  }, [])

  const statusVariant = (value: string) =>
    value === 'healthy' || value === 'connected' ? 'default' : 'destructive'

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold tracking-tight">System Health</h1>
          <p className="text-muted-foreground">
            Live status of backend services
          </p>
        </div>
        <Button onClick={fetchHealth} variant="outline" disabled={loading}>
          {loading ? 'Checking...' : 'Refresh'}
        </Button>
      </div>

      {error && (
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive">
              Connection Error
            </CardTitle>
            <CardDescription>{error}</CardDescription>
          </CardHeader>
        </Card>
      )}

      {health && (
        <div className="grid gap-6 sm:grid-cols-3">
          <Card>
            <CardHeader>
              <CardDescription>Overall Status</CardDescription>
              <CardTitle className="flex items-center gap-2">
                <Badge
                  variant={statusVariant(health.status)}
                  data-testid="status-badge"
                >
                  {health.status}
                </Badge>
              </CardTitle>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <CardDescription>Redis Cache</CardDescription>
              <CardTitle className="flex items-center gap-2">
                <Badge
                  variant={statusVariant(health.redis)}
                  data-testid="redis-badge"
                >
                  {health.redis}
                </Badge>
              </CardTitle>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <CardDescription>API Version</CardDescription>
              <CardTitle data-testid="version-text">
                v{health.version}
              </CardTitle>
            </CardHeader>
          </Card>
        </div>
      )}

      {!loading && !error && !health && (
        <Card>
          <CardContent className="py-8 text-center text-muted-foreground">
            No health data available.
          </CardContent>
        </Card>
      )}
    </div>
  )
}
