import { useState, useEffect, useCallback } from 'react'
import { getComments, createComment, deleteComment } from '../api/comments.api.js'

const useComments = (postId) => {
  const [comments, setComments] = useState([])
  const [loading,  setLoading]  = useState(false)
  const [error,    setError]    = useState(null)

  useEffect(() => {
    if (!postId) return
    setLoading(true)
    getComments(postId)
      .then(({ data }) => setComments(data.items))
      .catch((err) => setError(err.response?.data?.detail ?? 'Erreur chargement commentaires.'))
      .finally(() => setLoading(false))
  }, [postId])

  const addComment = useCallback(async (content) => {
    const { data } = await createComment(postId, content)
    setComments((prev) => [...prev, data])
    return data
  }, [postId])

  const removeComment = useCallback(async (commentId) => {
    await deleteComment(commentId)
    setComments((prev) => prev.filter((c) => c.id !== commentId))
  }, [])

  // Appelé par usePostSocket pour les événements temps réel
  const applyRealtimeEvent = useCallback((event) => {
    if (event.type === 'comment.created') {
      // Évite le doublon si l'auteur est l'utilisateur courant (déjà ajouté optimistiquement)
      setComments((prev) =>
        prev.some((c) => c.id === event.payload.id)
          ? prev
          : [...prev, event.payload],
      )
    }
    if (event.type === 'comment.deleted') {
      setComments((prev) => prev.filter((c) => c.id !== event.payload.id))
    }
  }, [])

  return { comments, loading, error, addComment, removeComment, applyRealtimeEvent }
}

export default useComments
