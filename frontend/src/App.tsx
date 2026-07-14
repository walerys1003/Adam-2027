import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom'
import { AuthProvider } from '@/lib/auth/AuthContext'
import { RequireAuth } from '@/lib/auth/RequireAuth'
import { LandingPage } from '@/pages/LandingPage'
import { DesignSystemPage } from '@/pages/DesignSystemPage'
import { LoginPage } from '@/pages/LoginPage'

function LandingRoute() {
  const navigate = useNavigate()
  return <LandingPage onLogin={() => navigate('/login')} onOrder={() => navigate('/login')} />
}

// Temporary placeholders — replaced in ETAP 4 / 5
function PanelPlaceholder() {
  return (
    <div className="min-h-screen grid place-items-center bg-paper">
      <div className="text-center">
        <span className="eyebrow">Panel Opiekuna</span>
        <h1 className="font-serif text-h2 text-granat-900 mt-1">Wkrótce (ETAP 4)</h1>
      </div>
    </div>
  )
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
                <PanelPlaceholder />
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
