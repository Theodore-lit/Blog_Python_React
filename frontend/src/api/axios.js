import axios from 'axios'
import tokenService from '../services/token.service.js'

const instance = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Intercepteur requête — injecte le token si présent
instance.interceptors.request.use((config) => {
  const token = tokenService.getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Intercepteur réponse — redirige vers /login sur 401
instance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      tokenService.clearToken()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

export default instance
