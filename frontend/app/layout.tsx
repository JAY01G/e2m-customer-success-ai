import type { Metadata } from 'next';
import './globals.css';
import { ReduxProvider } from '@/components/providers/ReduxProvider';
import { ToastProvider } from '@/components/providers/ToastProvider';

export const metadata: Metadata = {
  title: 'SuccessAI — Enterprise Customer Success Platform',
  description: 'AI-Powered Customer Success Platform with automated interaction insights, health scoring, and predictive risk detection.',
  icons: {
    icon: [
      { url: '/favicon.svg', type: 'image/svg+xml' },
    ],
    apple: [
      { url: '/favicon.svg', type: 'image/svg+xml' },
    ],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        <ReduxProvider>
          <ToastProvider>{children}</ToastProvider>
        </ReduxProvider>
      </body>
    </html>
  );
}

