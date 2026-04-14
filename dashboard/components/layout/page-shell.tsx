'use client';

import { Sidebar } from './sidebar';
import { Topbar } from './topbar';

interface PageShellProps {
  title: string;
  breadcrumb?: string;
  children: React.ReactNode;
  notificationCount?: number;
}

export const PageShell = ({
  title,
  breadcrumb,
  children,
  notificationCount = 0,
}: PageShellProps) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <div className="ml-64">
        <Topbar
          title={title}
          breadcrumb={breadcrumb}
          notificationCount={notificationCount}
        />
        <main className="pt-24 pb-8 px-8">
          {children}
        </main>
      </div>
    </div>
  );
};
