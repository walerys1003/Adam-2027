import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom'
import { AuthProvider } from '@/lib/auth/AuthContext'
import { RequireAuth } from '@/lib/auth/RequireAuth'
import { LandingPage } from '@/pages/LandingPage'
import { DesignSystemPage } from '@/pages/DesignSystemPage'
import { LoginPage } from '@/pages/LoginPage'
import { DashboardPage } from '@/pages/panel/DashboardPage'

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
          <Route
            path="/panel/*"
            element={
              <RequireAuth permission="panel:caregiver">
                <DashboardPage />
              </RequireAuth>
            }
          />
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
