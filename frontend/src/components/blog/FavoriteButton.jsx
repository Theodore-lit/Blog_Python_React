import React from 'react'
import useFavorite from '../../hooks/useFavorite.js'

/**
 * Affichage pur du bouton favori.
 * Toute la logique (optimiste, rollback) vit dans useFavorite.
 */
const FavoriteButton = ({ postId }) => {
  const { favorited, loading, toggle } = useFavorite(postId)

  return (
    <button
      onClick={toggle}
      disabled={loading}
      aria-label={favorited ? 'Retirer des favoris' : 'Ajouter aux favoris'}
      style={{
        background: favorited ? '#d69e2e' : '#eee',
        color:      favorited ? '#fff'    : '#333',
        border: 'none',
        borderRadius: 6,
        padding: '0.4rem 0.9rem',
        fontWeight: 600,
      }}
    >
      {favorited ? '★' : '☆'} Favori
    </button>
  )
}

export default FavoriteButton
