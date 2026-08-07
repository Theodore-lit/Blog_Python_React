import api from './axios.js'

export const toggleFavorite = (postId) =>
  api.post(`/api/posts/${postId}/favorite`)

export const getMyFavorites = (skip = 0, limit = 20) =>
  api.get('/api/me/favorites', { params: { skip, limit } })
