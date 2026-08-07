import { useState, useEffect } from 'react'
import { getPost } from '../api/posts.api.js'

const useFetchPost = (id) => {
  const [post,    setPost]    = useState(null)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)

  useEffect(() => {
    if (!id) return
    let cancelled = false

    const fetch = async () => {
      setLoading(true)
      setError(null)
      try {
        const { data } = await getPost(id)
        if (!cancelled) setPost(data)
      } catch (err) {
        if (!cancelled)
          setError(err.response?.data?.detail ?? 'Post introuvable.')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    fetch()
    return () => { cancelled = true }
  }, [id])

  return { post, loading, error }
}

export default useFetchPost
