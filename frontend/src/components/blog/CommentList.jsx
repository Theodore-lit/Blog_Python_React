import React, { useState } from 'react'
import useComments from '../../hooks/useComments.js'
import useAuth from '../../hooks/useAuth.js'
import CommentItem from './CommentItem.jsx'
import BaseInput from '../ui/BaseInput.jsx'
import BaseButton from '../ui/BaseButton.jsx'

const CommentList = ({ postId, socketRef }) => {
  const { comments, loading, error, addComment, removeComment, applyRealtimeEvent } =
    useComments(postId)
  const { user, isAuthenticated } = useAuth()
  const [content, setContent] = useState('')
  const [busy,    setBusy]    = useState(false)

  if (socketRef) socketRef.current = applyRealtimeEvent

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!content.trim()) return
    setBusy(true)
    try { await addComment(content); setContent('') }
    finally { setBusy(false) }
  }

  return (
    <section style={{ marginTop: '2rem' }}>
      <h3 style={{ marginBottom: '0.75rem' }}>Commentaires ({comments.length})</h3>

      {loading && <p>Chargement…</p>}
      {error   && <p style={{ color: '#e53e3e' }}>{error}</p>}

      {comments.map((c) => (
        <CommentItem
          key={c.id}
          comment={c}
          canDelete={user?.id === c.author?.id}
          onDelete={removeComment}
        />
      ))}

      {isAuthenticated && (
        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem', alignItems: 'flex-start' }}>
          <BaseInput
            id="new-comment"
            placeholder="Ajouter un commentaire…"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            style={{ marginBottom: 0 }}
          />
          <BaseButton type="submit" disabled={busy || !content.trim()}>
            {busy ? '…' : 'Envoyer'}
          </BaseButton>
        </form>
      )}
    </section>
  )
}

export default CommentList
