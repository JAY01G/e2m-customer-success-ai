/**
 * Sidebar Navigation Component.
 *
 * Renders main navigation links and AI telemetry engine status card.
 */

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { NavItem } from '@/types';
import {
  LayoutDashboard,
  Users,
  MessageSquare,
  UserCheck,
  Sparkles,
} from 'lucide-react';

/**
 * Desktop sidebar navigation bar with active route highlighting.
 */
export const Sidebar: React.FC = () => {
  const pathname = usePathname();

  const navItems: NavItem[] = [
    {
      label: 'Dashboard',
      href: '/dashboard',
      icon: <LayoutDashboard className="h-4 w-4" />,
    },
    {
      label: 'Customers',
      href: '/customers',
      icon: <Users className="h-4 w-4" />,
    },
    {
      label: 'Interactions',
      href: '/interactions',
      icon: <MessageSquare className="h-4 w-4" />,
    },
    {
      label: 'Profile & RBAC',
      href: '/profile',
      icon: <UserCheck className="h-4 w-4" />,
    },
  ];

  return (
    <aside className="hidden lg:flex w-64 flex-col justify-between border-r border-border/80 bg-card/40 p-4 backdrop-blur-md">
      <div className="space-y-6">
        <div className="space-y-1">
          <span className="px-3 text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
            Platform Menu
          </span>
          <nav className="mt-2 space-y-1">
            {navItems.map((item) => {
              const isActive =
                pathname === item.href ||
                (item.href !== '/dashboard' && pathname.startsWith(item.href));

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold transition-all duration-200',
                    isActive
                      ? 'bg-primary text-primary-foreground shadow-glow font-bold'
                      : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                  )}
                >
                  {item.icon}
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>
      </div>

      {/* AI Telemetry Tag */}
      <div className="rounded-xl border border-indigo-500/20 bg-indigo-500/5 p-3.5 text-xs text-indigo-300">
        <div className="flex items-center gap-2 font-bold text-indigo-400">
          <Sparkles className="h-4 w-4" />
          <span>AI Engine Active</span>
        </div>
        <p className="mt-1 text-[11px] leading-relaxed text-muted-foreground">
          Autonomous sentiment classification, action items & risk detection
        </p>
      </div>
    </aside>
  );
};

