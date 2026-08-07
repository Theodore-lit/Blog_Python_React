import { useState, useEffect, useCallback } from 'react'
import { getPosts } from '../api/posts.api.js'

const useFetchPosts = () => {
  const [posts,    setPosts]   = useState([])
  const [total,    setTotal]   = useState(0)
  const [page,     setPage]    = useState(1)
  const [loading,  setLoading] = useState(false)
  const [error,    setError]   = useState(null)

  const fetch = useCallback(async (p = 1) => {
    setLoading(true)
    setError(null)
    try {
      const { data } = await getPosts(p)
      setPosts(data.items)
      setTotal(data.total)
      setPage(p)
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Erreur lors du chargement des posts.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetch(1) }, [fetch])

  return { posts, total, page, loading, error, fetchPage: fetch }
}

export default useFetchPosts
