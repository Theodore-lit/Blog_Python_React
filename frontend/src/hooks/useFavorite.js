import { useState, useCallback, useRef } from 'react'
import { toggleFavorite } from '../api/favorites.api.js'

// Pas de chargement initial de l'état "favorited" : l'API ne fournit pas
// d'endpoint GET pour l'état d'un seul favori — on part de false et on
// laisse le toggle serveur faire autorité.
const useFavorite = (postId) => {
  const [favorited, setFavorited] = useState(false)
  const [loading,   setLoading]   = useState(false)
  const snapshot = useRef(null)

  const toggle = useCallback(async () => {
    // Mise à jour optimiste
    snapshot.current = favorited
    setFavorited((v) => !v)
    setLoading(true)
    try {
      const { data } = await toggleFavorite(postId)
      setFavorited(data.favorited)
    } catch {
      // Rollback
      setFavorited(snapshot.current)
    } finally {
      setLoading(false)
      snapshot.current = null
    }
  }, [postId, favorited])

  return { favorited, loading, toggle }
}

export default useFavorite
