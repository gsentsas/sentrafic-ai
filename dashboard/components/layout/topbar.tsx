'use client';

import { Bell, User } from 'lucide-react';
import { getUserFromToken } from '@/lib/auth';

interface TopbarProps {
  title: string;
  breadcrumb?: string;
  notificationCount?: number;
}

export const Topbar = ({
  title,
  breadcrumb,
  notificationCount = 0,
}: TopbarProps) => {
  const user = getUserFromToken();

  return (
    <div className="fixed top-0 left-64 right-0 h-16 bg-white border-b border-gray-200 flex items-center justify-between px-8 z-40">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
        {breadcrumb && <p className="text-sm text-gray-600">{breadcrumb}</p>}
      </div>

      <div className="flex items-center gap-6">
        {/* Notifications */}
        <button className="relative p-2 text-gray-600 hover:text-gray-900 transition-colors">
          <Bell className="w-5 h-5" />
          {notificationCount > 0 && (
            <span className="absolute top-1 right-1 h-2 w-2 bg-danger rounded-full" />
          )}
        </button>

        {/* User Avatar */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-primary/20 flex items-center justify-center">
            <User className="w-5 h-5 text-primary" />
          </div>
          {user && (
            <div className="hidden md:block">
              <p className="text-sm font-medium text-gray-900">{user.fullName}</p>
              <p className="text-xs text-gray-600">{user.role}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
