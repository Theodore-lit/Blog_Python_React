// Seul point d'accès à localStorage pour le JWT.
// Aucun composant ni hook ne doit lire/écrire localStorage directement.

const KEY = 'auth_token'

const getToken = () => localStorage.getItem(KEY)

const setToken = (token) => localStorage.setItem(KEY, token)

const clearToken = () => localStorage.removeItem(KEY)

export default { getToken, setToken, clearToken }
