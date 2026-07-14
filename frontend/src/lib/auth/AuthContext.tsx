import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import type { User } from '@/types/domain'
import { api, tokenStore, type LoginPayload } from '@/lib/api/client'
import { can, type Permission } from './rbac'

interface AuthState {
  user: User | null
  loading: boolean
  login: (payload: LoginPayload) => Promise<User>
  logout: () => void
  can: (permission: Permission) => boolean
}

const AuthCtx = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  // Rehydrate session from stored token
  useEffect(() => {
    const token = tokenStore.get()
    if (token) {
      const decoded = api.decodeToken(token)
      if (decoded) setUser(decoded)
    }
    setLoading(false)
  }, [])

  const login = async (payload: LoginPayload): Promise<User> => {
    const res = await api.login(payload)
    tokenStore.set(res.accessToken, res.refreshToken)
    setUser(res.user)
    return res.user
  }

  const logout = () => {
    tokenStore.clear()
    setUser(null)
  }

  const value = useMemo<AuthState>(
    () => ({
      user,
      loading,
      login,
      logout,
      can: (permission: Permission) => can(user?.role, permission),
    }),
    [user, loading],
  )

  return <AuthCtx.Provider value={value}>{children}</AuthCtx.Provider>
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthCtx)
  if (!ctx) throw new Error('useAuth must be used within <AuthProvider>')
  return ctx
}
