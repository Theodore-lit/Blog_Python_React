import React from 'react'
import useLike from '../../hooks/useLike.js'

/**
 * Affichage pur du bouton like + compteur.
 * Toute la logique (optimiste, rollback, WS) vit dans useLike.
 *
 * socketRef : ref transmise par PostDetail → usePostSocket appellera
 * socketRef.current(event) pour notifier ce composant des likes externes.
 */
const LikeButton = ({ postId, socketRef }) => {
  const { liked, count, loading, toggle, applyRealtimeEvent } = useLike(postId)

  // Expose applyRealtimeEvent au parent pour le branchement WebSocket (étape 7)
  if (socketRef) socketRef.current = applyRealtimeEvent

  return (
    <button
      onClick={toggle}
      disabled={loading}
      aria-label={liked ? 'Retirer le like' : 'Liker ce post'}
      style={{
        background: liked ? '#e53e3e' : '#eee',
        color:      liked ? '#fff'    : '#333',
        border: 'none',
        borderRadius: 6,
        padding: '0.4rem 0.9rem',
        fontWeight: 600,
      }}
    >
      {liked ? '♥' : '♡'} {count}
    </button>
  )
}

export default LikeButton
