import React, { useState, useEffect } from 'react'
import { getMyFavorites } from '../api/favorites.api.js'
import PostCard from '../components/blog/PostCard.jsx'

const LIMIT = 20

const Favorites = () => {
  const [posts,   setPosts]   = useState([])
  const [total,   setTotal]   = useState(0)
  const [page,    setPage]    = useState(1)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)

  useEffect(() => {
    setLoading(true)
    setError(null)
    getMyFavorites((page - 1) * LIMIT, LIMIT)
      .then(({ data }) => { setPosts(data.items); setTotal(data.total) })
      .catch((err) => setError(err.response?.data?.detail ?? 'Erreur chargement favoris.'))
      .finally(() => setLoading(false))
  }, [page])

  const totalPages = Math.ceil(total / LIMIT)

  return (
    <div>
      <h1>Mes favoris</h1>

      {loading && <p>Chargement…</p>}
      {error   && <p style={{ color: 'red' }}>{error}</p>}
      {!loading && posts.length === 0 && <p>Aucun favori pour l'instant.</p>}

      {posts.map((post) => <PostCard key={post.id} post={post} />)}

      {totalPages > 1 && (
        <nav style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
          <button disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>←</button>
          <span>{page} / {totalPages}</span>
          <button disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>→</button>
        </nav>
      )}
    </div>
  )
}

export default Favorites
