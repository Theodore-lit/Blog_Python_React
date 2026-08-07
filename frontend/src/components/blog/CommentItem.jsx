import React from 'react'
import { formatDateTime } from '../../utils/formatDate.js'

/**
 * Affichage pur d'un commentaire.
 * La logique de suppression (appel API) reste dans useComments,
 * déclenchée par le callback onDelete transmis par CommentList.
 */
const CommentItem = ({ comment, canDelete, onDelete }) => (
  <div style={{ borderTop: '1px solid #eee', padding: '0.75rem 0' }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#666' }}>
      <strong>{comment.author?.username ?? '—'}</strong>
      <span>{formatDateTime(comment.created_at)}</span>
    </div>
    <p style={{ marginTop: '0.25rem' }}>{comment.content}</p>
    {canDelete && (
      <button
        onClick={() => onDelete(comment.id)}
        style={{ fontSize: '0.75rem', color: 'red', background: 'none', border: 'none', padding: 0, marginTop: '0.25rem' }}
      >
        Supprimer
      </button>
    )}
  </div>
)

export default CommentItem
