import api from './axios.js'

export const getComments = (postId, skip = 0, limit = 50) =>
  api.get(`/api/posts/${postId}/comments`, { params: { skip, limit } })

export const createComment = (postId, content) =>
  api.post(`/api/posts/${postId}/comments`, { content })

export const deleteComment = (commentId) =>
  api.delete(`/api/comments/${commentId}`)
