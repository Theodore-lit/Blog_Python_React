import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import useAuth from '../hooks/useAuth.js'
import BaseInput from '../components/ui/BaseInput.jsx'
import BaseButton from '../components/ui/BaseButton.jsx'

const Register = () => {
  const { register }            = useAuth()
  const navigate                = useNavigate()
  const [username, setUsername] = useState('')
  const [email,    setEmail]    = useState('')
  const [pass,     setPass]     = useState('')
  const [error,    setError]    = useState(null)
  const [busy,     setBusy]     = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await register(username, email, pass)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail ?? "Erreur lors de l'inscription.")
    } finally {
      setBusy(false)
    }
  }

  return (
    <div style={{ maxWidth: 420, margin: '3rem auto' }}>
      <h1 style={{ marginBottom: '1.5rem' }}>Inscription</h1>
      <form onSubmit={handleSubmit}>
        <BaseInput
          id="username" type="text" label="Nom d'utilisateur"
          placeholder="alice" required
          value={username} onChange={(e) => setUsername(e.target.value)}
        />
        <BaseInput
          id="email" type="email" label="Email"
          placeholder="vous@exemple.com" required
          value={email} onChange={(e) => setEmail(e.target.value)}
        />
        <BaseInput
          id="password" type="password" label="Mot de passe"
          placeholder="••••••••" required
          value={pass} onChange={(e) => setPass(e.target.value)}
        />
        {error && <p style={{ color: '#e53e3e', marginBottom: '0.75rem' }}>{error}</p>}
        <BaseButton type="submit" disabled={busy} style={{ width: '100%' }}>
          {busy ? 'Inscription…' : "S'inscrire"}
        </BaseButton>
      </form>
      <p style={{ marginTop: '1rem' }}>
        Déjà un compte ? <Link to="/login">Se connecter</Link>
      </p>
    </div>
  )
}

export default Register
