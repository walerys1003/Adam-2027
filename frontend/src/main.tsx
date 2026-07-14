import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/tokens.css'
import './styles/globals.css'
import App from './App'
import { initNativeShell } from '@/lib/native'

// Inicjalizacja powłoki natywnej (Capacitor) — no-op w web/PWA
void initNativeShell()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
