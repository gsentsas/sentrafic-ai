'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import clsx from 'clsx';
import { LogOut, Activity } from 'lucide-react';
import { NAV_ITEMS, APP_NAME } from '@/lib/constants';
import { getUserFromToken, logout } from '@/lib/auth';
import { Button } from '@/components/ui/button';

export const Sidebar = () => {
  const pathname = usePathname();
  const router = useRouter();
  const user = getUserFromToken();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <aside className="fixed left-0 top-0 w-64 h-screen bg-sidebar text-white flex flex-col">
      {/* Logo */}
      <div className="px-6 py-8 border-b border-white/10 flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center">
          <Activity className="w-6 h-6 text-white" />
        </div>
        <h1 className="text-xl font-bold">{APP_NAME}</h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-8 space-y-2">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                'flex items-center gap-3 px-4 py-3 rounded-lg transition-all relative',
                isActive
                  ? 'bg-white/10 text-white'
                  : 'text-gray-300 hover:text-white hover:bg-white/5'
              )}
            >
              {isActive && (
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary rounded-r" />
              )}
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Divider */}
      <div className="px-4 py-4 border-t border-white/10" />

      {/* User Info */}
      <div className="px-4 py-4 border-b border-white/10">
        {user && (
          <div className="mb-4">
            <p className="text-sm text-gray-400">Logged in as</p>
            <p className="font-medium text-white truncate">{user.fullName}</p>
            <p className="text-xs text-gray-400 truncate">{user.email}</p>
          </div>
        )}
        <Button
          variant="ghost"
          size="sm"
          onClick={handleLogout}
          className="w-full justify-start text-gray-300 hover:text-white"
        >
          <LogOut className="w-4 h-4 mr-2" />
          Logout
        </Button>
      </div>
    </aside>
  );
};
