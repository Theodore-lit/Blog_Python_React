import { useState, useEffect, useCallback, useRef } from 'react'
import { toggleLike, getLikeCount } from '../api/likes.api.js'

const useLike = (postId) => {
  const [liked,  setLiked]  = useState(false)
  const [count,  setCount]  = useState(0)
  const [loading, setLoading] = useState(false)
  // Snapshot avant mise à jour optimiste — permet le rollback
  const snapshot = useRef(null)

  useEffect(() => {
    if (!postId) return
    getLikeCount(postId).then(({ data }) => setCount(data.likes_count))
  }, [postId])

  const toggle = useCallback(async () => {
    // Mise à jour optimiste immédiate
    snapshot.current = { liked, count }
    setLiked((v) => !v)
    setCount((v) => liked ? v - 1 : v + 1)
    setLoading(true)
    try {
      const { data } = await toggleLike(postId)
      // Synchronise avec la vérité serveur
      setLiked(data.liked)
      setCount(data.likes_count)
    } catch {
      // Rollback si l'appel API échoue
      setLiked(snapshot.current.liked)
      setCount(snapshot.current.count)
    } finally {
      setLoading(false)
      snapshot.current = null
    }
  }, [postId, liked, count])

  // Appelé par usePostSocket pour rester synchronisé avec les likes d'autres users
  const applyRealtimeEvent = useCallback((event) => {
    if (event.type === 'like.created' || event.type === 'like.deleted') {
      setCount(event.payload.likes_count)
    }
  }, [])

  return { liked, count, loading, toggle, applyRealtimeEvent }
}

export default useLike
