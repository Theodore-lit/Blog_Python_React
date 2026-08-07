import React, { useRef } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import useFetchPost from '../hooks/useFetchPost.js'
import useAuth from '../hooks/useAuth.js'
import usePostSocket from '../hooks/usePostSocket.js'
import { deletePost } from '../api/posts.api.js'
import { formatDateTime } from '../utils/formatDate.js'
import CommentList from '../components/blog/CommentList.jsx'
import LikeButton from '../components/blog/LikeButton.jsx'
import FavoriteButton from '../components/blog/FavoriteButton.jsx'

const PostDetail = () => {
  const { id }                    = useParams()
  const navigate                  = useNavigate()
  const { post, loading, error }  = useFetchPost(id)
  const { user, isAuthenticated } = useAuth()

  // Refs exposant les callbacks temps réel de CommentList et LikeButton
  const commentSocketRef = useRef(null)
  const likeSocketRef    = useRef(null)

  // Tous les hooks AVANT les returns conditionnels (règle des hooks React)
  usePostSocket(post ? Number(id) : null, commentSocketRef, likeSocketRef)

  if (loading) return <p>Chargement…</p>
  if (error)   return <p style={{ color: 'red' }}>{error}</p>
  if (!post)   return null

  const isAuthor = user?.id === post.author?.id

  const handleDelete = async () => {
    if (!confirm('Supprimer ce post ?')) return
    await deletePost(id)
    navigate('/')
  }

  return (
    <article>
      <h1>{post.title}</h1>
      <p style={{ color: '#666', fontSize: '0.875rem' }}>
        Par <strong>{post.author?.username}</strong> · {formatDateTime(post.created_at)}
      </p>

      {isAuthor && (
        <div style={{ display: 'flex', gap: '0.5rem', margin: '0.5rem 0' }}>
          <Link to={`/posts/${id}/edit`}>Modifier</Link>
          <button onClick={handleDelete}>Supprimer</button>
        </div>
      )}

      <p style={{ margin: '1.5rem 0', whiteSpace: 'pre-wrap' }}>{post.content}</p>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
        {isAuthenticated && <LikeButton postId={Number(id)} socketRef={likeSocketRef} />}
        {isAuthenticated && <FavoriteButton postId={Number(id)} />}
      </div>

      <CommentList postId={Number(id)} socketRef={commentSocketRef} />
    </article>
  )
}

export default PostDetail
