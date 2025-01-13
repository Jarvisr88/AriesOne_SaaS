import { useCurrentTenant, useTenantStats } from '@/api/tenant'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Building2, Users, Database } from 'lucide-react'
import { formatBytes } from '@/lib/utils'

export function TenantDashboard() {
  const { data: tenant, isLoading: isTenantLoading, error: tenantError } = useCurrentTenant()
  const { data: stats, isLoading: isStatsLoading, error: statsError } = useTenantStats()

  if (tenantError || statsError) {
    return (
      <Alert variant="destructive">
        <AlertDescription>
          Failed to load tenant information. Please try again later.
        </AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">
          {isTenantLoading ? (
            <Skeleton className="h-9 w-[200px]" />
          ) : (
            tenant?.name
          )}
        </h2>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-muted-foreground">
            {tenant?.subscription_tier.toUpperCase()}
          </span>
          <span
            className={`inline-block h-2 w-2 rounded-full ${
              tenant?.status === 'active'
                ? 'bg-green-500'
                : tenant?.status === 'suspended'
                ? 'bg-red-500'
                : 'bg-yellow-500'
            }`}
          />
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Companies</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isStatsLoading ? (
              <Skeleton className="h-7 w-[100px]" />
            ) : (
              <div className="text-2xl font-bold">{stats?.company_count}</div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isStatsLoading ? (
              <Skeleton className="h-7 w-[100px]" />
            ) : (
              <div>
                <div className="text-2xl font-bold">
                  {stats?.active_user_count}
                </div>
                <p className="text-xs text-muted-foreground">
                  of {stats?.user_count} total users
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Storage Used</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isStatsLoading ? (
              <Skeleton className="h-7 w-[100px]" />
            ) : (
              <div className="text-2xl font-bold">
                {formatBytes(stats?.storage_usage || 0)}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
