import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import type { ReactNode } from 'react'
import {
  LayoutDashboard,
  Users,
  ShoppingBag,
  MessageSquare,
  FileText,
  UserCog,
  Settings,
  LifeBuoy,
  LogOut,
  Menu,
  X,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { useAuth } from '@/lib/auth/AuthContext'
import { ROLE_LABEL } from '@/lib/auth/rbac'
import { Avatar } from '@/components/ui'

interface NavItem {
  to: string
  label: string
  icon: ReactNode
  badge?: number
  end?: boolean
}

const NAV: NavItem[] = [
  { to: '/panel', label: 'Dashboard', icon: <LayoutDashboard size={19} />, end: true },
  { to: '/panel/seniors', label: 'Moi bliscy', icon: <Users size={19} />, badge: 5 },
  { to: '/panel/orders', label: 'Zamówienia', icon: <ShoppingBag size={19} />, badge: 3 },
  { to: '/panel/messages', label: 'Wiadomości', icon: <MessageSquare size={19} />, badge: 2 },
  { to: '/panel/reports', label: 'Raporty', icon: <FileText size={19} /> },
  { to: '/panel/account', label: 'Konto', icon: <UserCog size={19} /> },
  { to: '/panel/settings', label: 'Ustawienia', icon: <Settings size={19} /> },
  { to: '/panel/help', label: 'Pomoc', icon: <LifeBuoy size={19} /> },
]

// Bottom nav for mobile — 5 most-used
const MOBILE_NAV = NAV.filter((n) =>
  ['/panel', '/panel/seniors', '/panel/orders', '/panel/messages', '/panel/reports'].includes(n.to),
)

function SidebarLink({ item, onClick }: { item: NavItem; onClick?: () => void }) {
  return (
    <NavLink
      to={item.to}
      end={item.end}
      onClick={onClick}
      className={({ isActive }) =>
        cn(
          'flex items-center gap-3 px-3 py-2.5 rounded-md text-body transition-colors',
          isActive
            ? 'bg-granat-700 text-white'
            : 'text-ink-700 hover:bg-granat-50 hover:text-granat-900',
        )
      }
    >
      {item.icon}
      <span className="flex-1">{item.label}</span>
      {item.badge != null && (
        <span className="text-caption font-medium rounded-full bg-zloto-500 text-granat-900 px-1.5 min-w-5 text-center">
          {item.badge}
        </span>
      )}
    </NavLink>
  )
}

export function PanelLayout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [mobileOpen, setMobileOpen] = useState(false)

  const doLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-paper flex">
      {/* Desktop sidebar */}
      <aside className="hidden lg:flex flex-col w-60 shrink-0 border-r border-line bg-white">
        <div className="flex items-center gap-3 px-5 h-16 border-b border-line">
          <span className="relative grid place-items-center w-8 h-8 rounded-md bg-granat-700">
            <span className="absolute inset-1 border border-zloto-500 rounded-[3px]" />
            <span className="relative font-serif text-zloto-500 text-body">A</span>
          </span>
          <span className="font-serif text-h4 text-granat-900">Adam</span>
        </div>
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {NAV.map((item) => (
            <SidebarLink key={item.to} item={item} />
          ))}
        </nav>
        <div className="p-3 border-t border-line">
          <button
            onClick={doLogout}
            className="flex items-center gap-3 px-3 py-2.5 rounded-md text-body text-ink-700 hover:bg-sem-red-bg hover:text-sem-red w-full transition-colors"
          >
            <LogOut size={19} /> Wyloguj
          </button>
        </div>
      </aside>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div className="absolute inset-0 bg-granat-900/40" onClick={() => setMobileOpen(false)} />
          <aside className="relative w-64 bg-white flex flex-col animate-fade-in">
            <div className="flex items-center justify-between px-5 h-16 border-b border-line">
              <span className="font-serif text-h4 text-granat-900">Adam</span>
              <button onClick={() => setMobileOpen(false)}>
                <X size={22} className="text-ink-500" />
              </button>
            </div>
            <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
              {NAV.map((item) => (
                <SidebarLink key={item.to} item={item} onClick={() => setMobileOpen(false)} />
              ))}
            </nav>
            <div className="p-3 border-t border-line">
              <button onClick={doLogout} className="flex items-center gap-3 px-3 py-2.5 text-body text-sem-red w-full">
                <LogOut size={19} /> Wyloguj
              </button>
            </div>
          </aside>
        </div>
      )}

      {/* Main column */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <header className="sticky top-0 z-30 h-16 bg-paper/90 backdrop-blur border-b border-line flex items-center justify-between px-4 lg:px-8">
          <button className="lg:hidden text-ink-700" onClick={() => setMobileOpen(true)}>
            <Menu size={24} />
          </button>
          <div className="hidden lg:flex items-center gap-2 text-label text-ink-500">
            <span className="w-1.5 h-1.5 rounded-full bg-sem-green animate-sem-dot-pulse" />
            Live · Odświeżenie 14:22
          </div>
          <div className="flex items-center gap-3">
            <div className="text-right leading-tight hidden sm:block">
              <p className="text-label font-medium text-granat-900">{user?.name}</p>
              <p className="text-caption text-ink-500">{user ? ROLE_LABEL[user.role] : ''}</p>
            </div>
            <Avatar firstName={user?.name.split(' ')[0] ?? 'A'} lastName={user?.name.split(' ')[1] ?? 'A'} size="sm" />
          </div>
        </header>

        <main className="flex-1 p-4 lg:p-8 pb-24 lg:pb-8">{children}</main>
      </div>

      {/* Mobile bottom nav */}
      <nav className="lg:hidden fixed bottom-0 inset-x-0 z-40 bg-white border-t border-line flex justify-around py-2 pb-[max(0.5rem,env(safe-area-inset-bottom))]">
        {MOBILE_NAV.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              cn(
                'flex flex-col items-center gap-1 px-2 py-1 text-caption transition-colors',
                isActive ? 'text-granat-700' : 'text-ink-400',
              )
            }
          >
            <span className="relative">
              {item.icon}
              {item.badge != null && (
                <span className="absolute -top-1 -right-2 text-[9px] rounded-full bg-zloto-500 text-granat-900 px-1">
                  {item.badge}
                </span>
              )}
            </span>
            {item.label.split(' ')[0]}
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
