import React from 'react'
import { Link } from 'react-router-dom'
import { formatDate } from '../../utils/formatDate.js'

/**
 * Affichage pur d'une carte post.
 * Ne fait aucun appel API — reçoit tout en props.
 */
const PostCard = ({ post }) => (
  <article style={{ border: '1px solid #ddd', borderRadius: 8, padding: '1rem', marginBottom: '1rem' }}>
    <h2>
      <Link to={`/posts/${post.id}`}>{post.title}</Link>
    </h2>
    <p style={{ color: '#666', fontSize: '0.875rem' }}>
      Par <strong>{post.author?.username ?? '—'}</strong> · {formatDate(post.created_at)}
    </p>
    <p style={{ marginTop: '0.5rem' }}>
      {post.content.length > 160 ? `${post.content.slice(0, 160)}…` : post.content}
    </p>
  </article>
)

export default PostCard
