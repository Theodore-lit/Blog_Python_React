import React from 'react'
import { Navigate, Outlet } from 'react-router-dom'
import useAuth from '../hooks/useAuth.js'

// Bloque l'accès à /login et /register si déjà connecté.
const PublicRoute = () => {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) return null
  return isAuthenticated ? <Navigate to="/" replace /> : <Outlet />
}

export default PublicRoute
