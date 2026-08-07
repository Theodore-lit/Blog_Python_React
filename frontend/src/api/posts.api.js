import api from './axios.js'

export const getPosts = (page = 1, limit = 20) =>
  api.get('/api/posts', { params: { skip: (page - 1) * limit, limit } })

export const getPost = (id) =>
  api.get(`/api/posts/${id}`)

export const createPost = (data) =>
  api.post('/api/posts', data)

export const updatePost = (id, data) =>
  api.put(`/api/posts/${id}`, data)

export const deletePost = (id) =>
  api.delete(`/api/posts/${id}`)
