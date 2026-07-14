import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { ArrowRight, ShieldCheck } from 'lucide-react'
import { useAuth } from '@/lib/auth/AuthContext'
import { Button } from '@/components/ui'

const DEMO = [
  { email: 'admin@silvertech.pl', role: 'Administrator → Panel Admina' },
  { email: 'anna@silvertech.pl', role: 'Opiekun → Panel Opiekuna' },
  { email: 'rodzina@gmail.com', role: 'Rodzina → Panel Opiekuna' },
]

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const from = (location.state as { from?: string })?.from ?? '/panel'

  const [email, setEmail] = useState('anna@silvertech.pl')
  const [password, setPassword] = useState('demo1234')
  const [otp, setOtp] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      const user = await login({ email, password, otpCode: otp })
      navigate(user.role === 'admin' ? '/admin' : from, { replace: true })
    } catch {
      setError('Nie udało się zalogować. Spróbuj ponownie.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-paper">
      {/* Brand panel */}
      <div className="hidden lg:flex flex-col justify-between p-12 bg-granat-900 text-paper">
        <div className="flex items-center gap-3">
          <span className="relative grid place-items-center w-9 h-9 rounded-md bg-granat-700">
            <span className="absolute inset-1 border border-zloto-500 rounded-[3px]" />
            <span className="relative font-serif text-zloto-500">A</span>
          </span>
          <span className="font-serif text-h4 text-white">Adam</span>
        </div>
        <div>
          <p className="font-serif italic text-h2 text-white/95 leading-tight max-w-md">
            „Adam dzwoni codziennie o ósmej. Zawsze pyta, jak spałam."
          </p>
          <p className="font-mono text-caption tracking-[0.14em] uppercase text-white/50 mt-4">
            Halina W., 78 lat · Wilda, Poznań
          </p>
        </div>
        <p className="text-caption text-white/40">SilverTech Sp. z o.o. · Poznań · v7.4.2</p>
      </div>

      {/* Form */}
      <div className="flex items-center justify-center p-6 sm:p-12">
        <form onSubmit={submit} className="w-full max-w-sm">
          <span className="eyebrow">Panel</span>
          <h1 className="font-serif text-h2 text-granat-900 mt-1">Zaloguj się</h1>
          <p className="text-body text-ink-600 mt-2">Dostęp dla opiekunów i administratorów SilverTech.</p>

          <div className="space-y-4 mt-8">
            <label className="block">
              <span className="text-label text-ink-700">E-mail</span>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 w-full rounded-md border border-line bg-white px-3 py-2.5 text-body focus:border-granat-400"
                required
              />
            </label>
            <label className="block">
              <span className="text-label text-ink-700">Hasło</span>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 w-full rounded-md border border-line bg-white px-3 py-2.5 text-body focus:border-granat-400"
                required
              />
            </label>
            <label className="block">
              <span className="text-label text-ink-700 inline-flex items-center gap-1">
                <ShieldCheck size={13} /> Kod 2FA (opcjonalnie w demo)
              </span>
              <input
                type="text"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                placeholder="123456"
                className="mt-1 w-full rounded-md border border-line bg-white px-3 py-2.5 text-body font-mono tracking-widest focus:border-granat-400"
              />
            </label>
          </div>

          {error && <p className="text-label text-sem-red mt-3">{error}</p>}

          <Button type="submit" variant="primary" size="lg" fullWidth className="mt-6" disabled={busy}>
            {busy ? 'Logowanie…' : 'Zaloguj'} <ArrowRight size={16} />
          </Button>

          <div className="mt-8 rounded-md border border-line bg-paper-2 p-4">
            <p className="text-caption uppercase tracking-wide text-ink-400 mb-2">Konta demo (kliknij)</p>
            <div className="space-y-1.5">
              {DEMO.map((d) => (
                <button
                  key={d.email}
                  type="button"
                  onClick={() => setEmail(d.email)}
                  className="block w-full text-left text-label text-granat-700 hover:text-zloto-700"
                >
                  <span className="font-mono">{d.email}</span> — {d.role}
                </button>
              ))}
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}
