import api from './axios.js'

export const toggleLike = (postId) =>
  api.post(`/api/posts/${postId}/like`)

export const getLikeCount = (postId) =>
  api.get(`/api/posts/${postId}/likes/count`)
