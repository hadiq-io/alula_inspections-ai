'use client';

import ChatInterface from '@/components/ChatInterface';
import PinLogin, { useAuth } from '@/components/PinLogin';

export default function Home() {
  const { isAuthenticated, isLoading, login } = useAuth();

  // Show loading state while checking auth
  if (isLoading) {
    return (
      <main className="flex items-center justify-center h-screen bg-black">
        <div className="w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
      </main>
    );
  }

  // Show login if not authenticated
  if (!isAuthenticated) {
    return <PinLogin onSuccess={login} />;
  }

  return (
    <main>
      <ChatInterface />
    </main>
  );
}
