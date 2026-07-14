import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom'
import { LandingPage } from '@/pages/LandingPage'
import { DesignSystemPage } from '@/pages/DesignSystemPage'

function LandingRoute() {
  const navigate = useNavigate()
  return <LandingPage onLogin={() => navigate('/panel')} onOrder={() => navigate('/panel')} />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingRoute />} />
        <Route path="/design-system" element={<DesignSystemPage />} />
      </Routes>
    </BrowserRouter>
  )
}
