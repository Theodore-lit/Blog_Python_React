import React from 'react'
import { Link } from 'react-router-dom'
import useFetchPosts from '../hooks/useFetchPosts.js'
import PostCard from '../components/blog/PostCard.jsx'
import useAuth from '../hooks/useAuth.js'

const LIMIT = 20

const Home = () => {
  const { posts, total, page, loading, error, fetchPage } = useFetchPosts()
  const { isAuthenticated } = useAuth()

  const totalPages = Math.ceil(total / LIMIT)

  return (
    <div>
      <header style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
        <h1>Mini Blog</h1>
        {isAuthenticated && <Link to="/posts/new">+ Nouveau post</Link>}
      </header>

      {loading && <p>Chargement…</p>}
      {error   && <p style={{ color: 'red' }}>{error}</p>}

      {posts.map((post) => <PostCard key={post.id} post={post} />)}

      {totalPages > 1 && (
        <nav style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
          <button disabled={page <= 1} onClick={() => fetchPage(page - 1)}>←</button>
          <span>{page} / {totalPages}</span>
          <button disabled={page >= totalPages} onClick={() => fetchPage(page + 1)}>→</button>
        </nav>
      )}
    </div>
  )
}

export default Home
