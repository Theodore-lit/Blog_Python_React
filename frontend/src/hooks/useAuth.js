import { useContext } from 'react'
import { AuthContext } from '../context/AuthContext.jsx'

// Wrapper simple — évite d'importer AuthContext partout dans l'app.
const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth doit être utilisé dans <AuthProvider>')
  return ctx
}

export default useAuth
