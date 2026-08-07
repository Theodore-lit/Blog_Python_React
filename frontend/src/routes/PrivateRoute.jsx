import React from 'react'
import { Navigate, Outlet } from 'react-router-dom'
import useAuth from '../hooks/useAuth.js'

// Protège les routes nécessitant une authentification.
// Affiche un loader pendant la vérification initiale du token.
const PrivateRoute = () => {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) return <p>Vérification de la session…</p>
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />
}

export default PrivateRoute
