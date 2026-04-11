'use client';

import { PageShell } from '@/components/layout/page-shell';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { getUserFromToken } from '@/lib/auth';
import { Package, Bell, Lock } from 'lucide-react';

export default function SettingsPage() {
  const user = getUserFromToken();

  return (
    <PageShell title="Settings">
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900">
          System Settings
        </h2>
        <p className="text-gray-600">Manage your account and preferences</p>
      </div>

      {/* Profile Section */}
      <div className="max-w-2xl space-y-6">
        <Card header={
          <div className="flex items-center gap-2">
            <Lock className="w-5 h-5 text-gray-600" />
            <h3 className="font-semibold text-gray-900">Profile Information</h3>
          </div>
        }>
          <div className="space-y-4">
            <Input
              label="Full Name"
              type="text"
              value={user?.fullName || ''}
              disabled
            />
            <Input
              label="Email"
              type="email"
              value={user?.email || ''}
              disabled
            />
            <Input
              label="Role"
              type="text"
              value={user?.role || ''}
              disabled
            />
          </div>
        </Card>

        {/* Notification Preferences */}
        <Card header={
          <div className="flex items-center gap-2">
            <Bell className="w-5 h-5 text-gray-600" />
            <h3 className="font-semibold text-gray-900">Notifications</h3>
          </div>
        }>
          <div className="space-y-4">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                defaultChecked={true}
                className="w-4 h-4 rounded border-gray-300"
              />
              <span className="text-gray-700">Alert notifications</span>
            </label>
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                defaultChecked={true}
                className="w-4 h-4 rounded border-gray-300"
              />
              <span className="text-gray-700">Daily summary emails</span>
            </label>
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                defaultChecked={false}
                className="w-4 h-4 rounded border-gray-300"
              />
              <span className="text-gray-700">Marketing updates</span>
            </label>
          </div>
        </Card>

        {/* System Info */}
        <Card header={
          <div className="flex items-center gap-2">
            <Package className="w-5 h-5 text-gray-600" />
            <h3 className="font-semibold text-gray-900">System Information</h3>
          </div>
        }>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Dashboard Version</span>
              <span className="font-mono text-gray-900">1.0.0</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">API Version</span>
              <span className="font-mono text-gray-900">1.0.0</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Last Update</span>
              <span className="font-mono text-gray-900">2024-01-15</span>
            </div>
          </div>
        </Card>

        {/* Save Button */}
        <div className="flex justify-end">
          <Button variant="secondary">
            Save Settings
          </Button>
        </div>
      </div>
    </PageShell>
  );
}
