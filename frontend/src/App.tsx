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
import { AdminLayout } from '@/components/admin'
import {
  AdminDashboard,
  AdminSeniors,
  AdminSeniorDetail,
  AdminCalls,
  AdminScheduling,
  AdminAlerts,
  AdminMarketplace,
  AdminWizard,
  AdminAgents,
  AdminAgentDetail,
  AdminProviders,
  AdminPipelines,
  AdminContexts,
  AdminAudio,
  AdminTools,
  AdminMCP,
  AdminFleet,
  AdminFleetDetail,
  AdminEnvironment,
  AdminDocker,
  AdminAsterisk,
  AdminModels,
  AdminLogs,
  AdminTerminal,
} from '@/pages/admin'

function LandingRoute() {
  const navigate = useNavigate()
  return <LandingPage onLogin={() => navigate('/login')} onOrder={() => navigate('/login')} />
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

          {/* Panel Admina — 23 ekranów nested pod AdminLayout (light-only) */}
          <Route
            path="/admin"
            element={
              <RequireAuth permission="panel:admin">
                <AdminLayout />
              </RequireAuth>
            }
          >
            {/* Overview */}
            <Route index element={<AdminDashboard />} />
            <Route path="seniors" element={<AdminSeniors />} />
            <Route path="seniors/:id" element={<AdminSeniorDetail />} />
            <Route path="calls" element={<AdminCalls />} />
            <Route path="scheduling" element={<AdminScheduling />} />
            <Route path="alerts" element={<AdminAlerts />} />
            <Route path="marketplace" element={<AdminMarketplace />} />
            <Route path="wizard" element={<AdminWizard />} />
            {/* Konfiguracja / Core Config */}
            <Route path="agents" element={<AdminAgents />} />
            <Route path="agents/:id" element={<AdminAgentDetail />} />
            <Route path="providers" element={<AdminProviders />} />
            <Route path="pipelines" element={<AdminPipelines />} />
            <Route path="contexts" element={<AdminContexts />} />
            <Route path="audio" element={<AdminAudio />} />
            <Route path="tools" element={<AdminTools />} />
            <Route path="mcp" element={<AdminMCP />} />
            <Route path="fleet" element={<AdminFleet />} />
            <Route path="fleet/:id" element={<AdminFleetDetail />} />
            {/* System */}
            <Route path="environment" element={<AdminEnvironment />} />
            <Route path="docker" element={<AdminDocker />} />
            <Route path="asterisk" element={<AdminAsterisk />} />
            <Route path="models" element={<AdminModels />} />
            <Route path="logs" element={<AdminLogs />} />
            <Route path="terminal" element={<AdminTerminal />} />
            <Route path="*" element={<Navigate to="/admin" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
