import React, { createContext, useState, useEffect, useCallback } from 'react'
import * as authApi from '../api/auth.api.js'
import tokenService from '../services/token.service.js'

export const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser]         = useState(null)
  const [isLoading, setLoading] = useState(true)

  // Recharge l'utilisateur au montage si un token existe déjà
  useEffect(() => {
    const restore = async () => {
      if (!tokenService.getToken()) { setLoading(false); return }
      try {
        const { data } = await authApi.getMe()
        setUser(data)
      } catch {
        tokenService.clearToken()
      } finally {
        setLoading(false)
      }
    }
    restore()
  }, [])

  const login = useCallback(async (email, password) => {
    const { data } = await authApi.login(email, password)
    tokenService.setToken(data.access_token)
    const me = await authApi.getMe()
    setUser(me.data)
  }, [])

  const register = useCallback(async (username, email, password) => {
    await authApi.register(username, email, password)
    await login(email, password)
  }, [login])

  const logout = useCallback(() => {
    tokenService.clearToken()
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: !!user,
      isLoading,
      login,
      register,
      logout,
    }}>
      {children}
    </AuthContext.Provider>
  )
}
