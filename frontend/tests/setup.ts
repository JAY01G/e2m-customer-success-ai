import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock Next.js App Router hooks
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    prefetch: vi.fn(),
    back: vi.fn(),
  }),
  usePathname: () => '/dashboard',
  useParams: () => ({ id: '123-uuid' }),
  useSearchParams: () => new URLSearchParams(),
}));

// Mock ResizeObserver for Recharts ResponsiveContainer in jsdom
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};
