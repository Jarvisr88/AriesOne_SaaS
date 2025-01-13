import { useState } from 'react'
import { useUpdateCompany } from '@/api/tenant'
import { Company } from '@/types/tenant'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { toast } from 'sonner'

interface CompanySettingsProps {
  company: Company
}

export function CompanySettings({ company }: CompanySettingsProps) {
  const [settings, setSettings] = useState(company.settings)
  const [features, setFeatures] = useState(company.features)
  const updateCompany = useUpdateCompany(company.id)

  const handleSettingChange = (key: string, value: any) => {
    setSettings((prev) => ({ ...prev, [key]: value }))
  }

  const handleFeatureToggle = (key: string) => {
    setFeatures((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  const handleSave = async () => {
    try {
      await updateCompany.mutateAsync({
        settings,
        features
      })
      toast.success('Company settings updated successfully')
    } catch (error) {
      toast.error('Failed to update company settings')
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Company Settings</CardTitle>
          <CardDescription>
            Configure company-specific settings and preferences
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <div>
              <Label>Company Logo URL</Label>
              <Input
                value={settings.logoUrl || ''}
                onChange={(e) =>
                  handleSettingChange('logoUrl', e.target.value)
                }
                placeholder="https://example.com/logo.png"
              />
            </div>

            <div>
              <Label>Theme</Label>
              <Select
                value={settings.theme || 'light'}
                onValueChange={(value) => handleSettingChange('theme', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select theme" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="light">Light</SelectItem>
                  <SelectItem value="dark">Dark</SelectItem>
                  <SelectItem value="system">System</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Default Language</Label>
              <Select
                value={settings.language || 'en'}
                onValueChange={(value) => handleSettingChange('language', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select language" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="es">Spanish</SelectItem>
                  <SelectItem value="fr">French</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Timezone</Label>
              <Select
                value={settings.timezone || 'UTC'}
                onValueChange={(value) => handleSettingChange('timezone', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select timezone" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="UTC">UTC</SelectItem>
                  <SelectItem value="America/New_York">Eastern Time</SelectItem>
                  <SelectItem value="America/Chicago">Central Time</SelectItem>
                  <SelectItem value="America/Denver">Mountain Time</SelectItem>
                  <SelectItem value="America/Los_Angeles">Pacific Time</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Features</CardTitle>
          <CardDescription>
            Enable or disable company-specific features
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Advanced Analytics</Label>
              <div className="text-sm text-muted-foreground">
                Enable detailed analytics and reporting
              </div>
            </div>
            <Switch
              checked={features.advancedAnalytics || false}
              onCheckedChange={() => handleFeatureToggle('advancedAnalytics')}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Custom Branding</Label>
              <div className="text-sm text-muted-foreground">
                Allow custom branding and white-labeling
              </div>
            </div>
            <Switch
              checked={features.customBranding || false}
              onCheckedChange={() => handleFeatureToggle('customBranding')}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>API Access</Label>
              <div className="text-sm text-muted-foreground">
                Enable API access for integration
              </div>
            </div>
            <Switch
              checked={features.apiAccess || false}
              onCheckedChange={() => handleFeatureToggle('apiAccess')}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Audit Logging</Label>
              <div className="text-sm text-muted-foreground">
                Enable detailed audit logging
              </div>
            </div>
            <Switch
              checked={features.auditLogging || false}
              onCheckedChange={() => handleFeatureToggle('auditLogging')}
            />
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button
          onClick={handleSave}
          disabled={updateCompany.isPending}
        >
          {updateCompany.isPending ? 'Saving...' : 'Save Changes'}
        </Button>
      </div>
    </div>
  )
}
