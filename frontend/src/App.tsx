import { BrowserRouter, Routes, Route, useNavigate, Navigate } from 'react-router-dom'
import { AuthProvider } from '@/lib/auth/AuthContext'
import { RequireAuth } from '@/lib/auth/RequireAuth'
import { LandingPage } from '@/pages/LandingPage'
import { DesignSystemPage } from '@/pages/DesignSystemPage'
import { LoginPage } from '@/pages/LoginPage'
import { PanelLayout } from '@/components/panel/PanelLayout'
import { DashboardPage } from '@/pages/panel/DashboardPage'
import { SeniorsPage } from '@/pages/panel/SeniorsPage'
import { SeniorDetailPage } from '@/pages/panel/SeniorDetailPage'
import { OrdersPage } from '@/pages/panel/OrdersPage'
import { MessagesPage } from '@/pages/panel/MessagesPage'
import { ReportsPage } from '@/pages/panel/ReportsPage'
import { AccountPage } from '@/pages/panel/AccountPage'
import { SettingsPage } from '@/pages/panel/SettingsPage'
import { HelpPage } from '@/pages/panel/HelpPage'

function LandingRoute() {
  const navigate = useNavigate()
  return <LandingPage onLogin={() => navigate('/login')} onOrder={() => navigate('/login')} />
}

function AdminPlaceholder() {
  return (
    <div className="min-h-screen grid place-items-center bg-paper">
      <div className="text-center">
        <span className="eyebrow">Panel Admina</span>
        <h1 className="font-serif text-h2 text-granat-900 mt-1">Wkrótce (ETAP 5)</h1>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingRoute />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/design-system" element={<DesignSystemPage />} />

          {/* Panel Opiekuna — nested under shared PanelLayout */}
          <Route
            path="/panel"
            element={
              <RequireAuth permission="panel:caregiver">
                <PanelLayout />
              </RequireAuth>
            }
          >
            <Route index element={<DashboardPage />} />
            <Route path="seniors" element={<SeniorsPage />} />
            <Route path="senior/:id" element={<SeniorDetailPage />} />
            <Route path="orders" element={<OrdersPage />} />
            <Route path="messages" element={<MessagesPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="account" element={<AccountPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="help" element={<HelpPage />} />
            <Route path="*" element={<Navigate to="/panel" replace />} />
          </Route>

          <Route
            path="/admin/*"
            element={
              <RequireAuth permission="panel:admin">
                <AdminPlaceholder />
              </RequireAuth>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
