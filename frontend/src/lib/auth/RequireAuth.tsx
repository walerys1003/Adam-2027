import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from './AuthContext'
import type { Permission } from './rbac'

/** Route guard: requires auth + optional permission. */
export function RequireAuth({
  children,
  permission,
}: {
  children: ReactNode
  permission?: Permission
}) {
  const { user, loading, can } = useAuth()
  const location = useLocation()

  if (loading) {
    return (
      <div className="min-h-screen grid place-items-center bg-paper">
        <div className="flex flex-col items-center gap-3 text-ink-500">
          <span className="w-8 h-8 rounded-full border-2 border-granat-200 border-t-granat-700 animate-spin" />
          <span className="text-label">Ładowanie…</span>
        </div>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />
  }

  if (permission && !can(permission)) {
    return (
      <div className="min-h-screen grid place-items-center bg-paper px-6">
        <div className="adam-card p-8 max-w-md text-center">
          <span className="eyebrow">Brak dostępu</span>
          <h1 className="font-serif text-h3 text-granat-900 mt-2">403 · Odmowa dostępu</h1>
          <p className="text-body text-ink-700 mt-3">
            Twoja rola ({user.role}) nie ma uprawnień do tej sekcji.
          </p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}
