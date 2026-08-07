import api from './axios.js'

export const login = (email, password) =>
  api.post('/api/auth/login', { email, password })

export const register = (username, email, password) =>
  api.post('/api/auth/register', { username, email, password })

export const getMe = () =>
  api.get('/api/auth/me')
