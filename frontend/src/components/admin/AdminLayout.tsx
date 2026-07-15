import { useState } from 'react'
import { NavLink, useNavigate, Outlet } from 'react-router-dom'
import type { ReactNode } from 'react'
import {
  LayoutDashboard,
  Users,
  PhoneCall,
  CalendarClock,
  Siren,
  Store,
  Wand2,
  Bot,
  Server,
  GitBranch,
  Layers,
  AudioLines,
  Wrench,
  Plug,
  Watch,
  Settings2,
  Boxes,
  PhoneForwarded,
  Cpu,
  ScrollText,
  TerminalSquare,
  LogOut,
  Menu,
  X,
  ShieldCheck,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { useAuth } from '@/lib/auth/AuthContext'
import { Avatar } from '@/components/ui'
import { SkipLink } from '@/components/a11y/SkipLink'

interface NavItem {
  to: string
  label: string
  icon: ReactNode
  badge?: string
  end?: boolean
}
interface NavSection {
  title: string
  items: NavItem[]
}

const SECTIONS: NavSection[] = [
  {
    title: 'Overview',
    items: [
      { to: '/admin', label: 'Dashboard', icon: <LayoutDashboard size={18} />, end: true },
      { to: '/admin/seniors', label: 'Seniorzy', icon: <Users size={18} />, badge: '1247' },
      { to: '/admin/calls', label: 'Historia rozmów', icon: <PhoneCall size={18} />, badge: '18.4K' },
      { to: '/admin/scheduling', label: 'Harmonogram', icon: <CalendarClock size={18} /> },
      { to: '/admin/alerts', label: 'Alerty', icon: <Siren size={18} /> },
      { to: '/admin/marketplace', label: 'Marketplace', icon: <Store size={18} />, badge: 'NEW' },
      { to: '/admin/wizard', label: 'Setup Wizard', icon: <Wand2 size={18} /> },
    ],
  },
  {
    title: 'Konfiguracja',
    items: [
      { to: '/admin/agents', label: 'Agenci', icon: <Bot size={18} />, badge: '12' },
      { to: '/admin/providers', label: 'Providers', icon: <Server size={18} />, badge: '7' },
      { to: '/admin/pipelines', label: 'Pipelines', icon: <GitBranch size={18} />, badge: '4' },
      { to: '/admin/contexts', label: 'Contexts', icon: <Layers size={18} /> },
      { to: '/admin/audio', label: 'Audio Profiles', icon: <AudioLines size={18} />, badge: '3' },
      { to: '/admin/tools', label: 'Tools', icon: <Wrench size={18} />, badge: '47' },
      { to: '/admin/mcp', label: 'MCP Servers', icon: <Plug size={18} /> },
      { to: '/admin/fleet', label: 'Wearables Fleet', icon: <Watch size={18} />, badge: 'NEW' },
    ],
  },
  {
    title: 'System',
    items: [
      { to: '/admin/environment', label: 'Environment', icon: <Settings2 size={18} />, badge: '78' },
      { to: '/admin/docker', label: 'Docker Services', icon: <Boxes size={18} /> },
      { to: '/admin/asterisk', label: 'Asterisk', icon: <PhoneForwarded size={18} /> },
      { to: '/admin/models', label: 'Models', icon: <Cpu size={18} /> },
      { to: '/admin/logs', label: 'Live Logs', icon: <ScrollText size={18} /> },
      { to: '/admin/terminal', label: 'Terminal', icon: <TerminalSquare size={18} /> },
    ],
  },
]

function SideLink({ item, onClick }: { item: NavItem; onClick?: () => void }) {
  return (
    <NavLink
      to={item.to}
      end={item.end}
      onClick={onClick}
      className={({ isActive }) =>
        cn(
          'flex items-center gap-3 px-3 py-2 rounded-md text-label transition-colors',
          isActive ? 'bg-granat-700 text-white' : 'text-ink-700 hover:bg-granat-50 hover:text-granat-900',
        )
      }
    >
      {item.icon}
      <span className="flex-1">{item.label}</span>
      {item.badge && (
        <span
          className={cn(
            'text-caption font-medium rounded-full px-1.5',
            item.badge === 'NEW' ? 'bg-zloto-500 text-granat-900' : 'bg-paper-3 text-ink-500',
          )}
        >
          {item.badge}
        </span>
      )}
    </NavLink>
  )
}

function SidebarContent({ onNav }: { onNav?: () => void }) {
  return (
    <nav aria-label="Nawigacja administracyjna" className="flex-1 p-3 space-y-5 overflow-y-auto">
      {SECTIONS.map((sec) => (
        <div key={sec.title}>
          <p className="px-3 mb-1.5 text-caption uppercase tracking-caps text-ink-400">{sec.title}</p>
          <div className="space-y-0.5">
            {sec.items.map((it) => (
              <SideLink key={it.to} item={it} onClick={onNav} />
            ))}
          </div>
        </div>
      ))}
    </nav>
  )
}

export function AdminLayout({ children }: { children?: ReactNode }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [mobileOpen, setMobileOpen] = useState(false)

  const doLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-paper flex">
      <SkipLink />
      {/* Desktop sidebar */}
      <aside aria-label="Menu administracyjne" className="hidden lg:flex flex-col w-64 shrink-0 border-r border-line bg-white">
        <div className="flex items-center gap-3 px-5 h-16 border-b border-line">
          <span className="relative grid place-items-center w-8 h-8 rounded-md bg-granat-700">
            <span className="absolute inset-1 border border-zloto-500 rounded-[3px]" />
            <span className="relative font-serif text-zloto-500 text-body">A</span>
          </span>
          <div className="leading-tight">
            <span className="font-serif text-h4 text-granat-900">Adam</span>
            <span className="block text-caption text-ink-400 uppercase tracking-caps">Admin Console</span>
          </div>
        </div>
        <SidebarContent />
        <div className="p-3 border-t border-line">
          <button
            onClick={doLogout}
            className="flex items-center gap-3 px-3 py-2 rounded-md text-label text-ink-700 hover:bg-sem-red-bg hover:text-sem-red w-full transition-colors"
          >
            <LogOut size={18} /> Wyloguj
          </button>
        </div>
      </aside>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div className="absolute inset-0 bg-granat-900/40" onClick={() => setMobileOpen(false)} />
          <aside className="relative w-72 bg-white flex flex-col animate-fade-in">
            <div className="flex items-center justify-between px-5 h-16 border-b border-line">
              <span className="font-serif text-h4 text-granat-900">Adam · Admin</span>
              <button onClick={() => setMobileOpen(false)}>
                <X size={22} className="text-ink-500" />
              </button>
            </div>
            <SidebarContent onNav={() => setMobileOpen(false)} />
            <div className="p-3 border-t border-line">
              <button onClick={doLogout} className="flex items-center gap-3 px-3 py-2 text-label text-sem-red w-full">
                <LogOut size={18} /> Wyloguj
              </button>
            </div>
          </aside>
        </div>
      )}

      {/* Main column */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="sticky top-0 z-30 h-16 bg-paper/90 backdrop-blur border-b border-line flex items-center justify-between px-4 lg:px-8">
          <button className="lg:hidden text-ink-700" onClick={() => setMobileOpen(true)}>
            <Menu size={24} />
          </button>
          <div className="hidden lg:flex items-center gap-2 text-label text-ink-500">
            <span className="w-1.5 h-1.5 rounded-full bg-sem-green animate-sem-dot-pulse" />
            System operacyjny · AVA v7.3.2 · Adam build
          </div>
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-1.5 text-caption text-ink-500">
              <ShieldCheck size={14} className="text-sem-green" /> 2FA
            </span>
            <div className="text-right leading-tight hidden sm:block">
              <p className="text-label font-medium text-granat-900">{user?.name}</p>
              <p className="text-caption text-ink-500">Administrator</p>
            </div>
            <Avatar firstName={user?.name.split(' ')[0] ?? 'A'} lastName={user?.name.split(' ')[1] ?? 'A'} size="sm" />
          </div>
        </header>

        <main id="main-content" tabIndex={-1} className="flex-1 p-4 lg:p-8 focus:outline-none">{children ?? <Outlet />}</main>
      </div>
    </div>
  )
}
