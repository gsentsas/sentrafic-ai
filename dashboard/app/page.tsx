'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '@/lib/auth';
import { LoadingState } from '@/components/ui/loading-state';

export default function RootPage() {
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated()) {
      router.push('/overview');
    } else {
      router.push('/login');
    }
  }, [router]);

  return <LoadingState message="Redirecting..." />;
}
