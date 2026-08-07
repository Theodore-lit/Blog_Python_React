import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getPost, createPost, updatePost } from '../api/posts.api.js'
import BaseInput from '../components/ui/BaseInput.jsx'
import BaseButton from '../components/ui/BaseButton.jsx'

const PostForm = () => {
  const { id }              = useParams()
  const navigate            = useNavigate()
  const isEdit              = Boolean(id)
  const [title,   setTitle]   = useState('')
  const [content, setContent] = useState('')
  const [error,   setError]   = useState(null)
  const [busy,    setBusy]    = useState(false)

  useEffect(() => {
    if (!isEdit) return
    getPost(id).then(({ data }) => {
      setTitle(data.title)
      setContent(data.content)
    })
  }, [id, isEdit])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      if (isEdit) {
        await updatePost(id, { title, content })
        navigate(`/posts/${id}`)
      } else {
        const { data } = await createPost({ title, content })
        navigate(`/posts/${data.id}`)
      }
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Erreur lors de la sauvegarde.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div style={{ maxWidth: 680, margin: '2rem auto' }}>
      <h1 style={{ marginBottom: '1.5rem' }}>{isEdit ? 'Modifier le post' : 'Nouveau post'}</h1>
      <form onSubmit={handleSubmit}>
        <BaseInput
          id="title" type="text" label="Titre"
          placeholder="Mon super article" required
          value={title} onChange={(e) => setTitle(e.target.value)}
        />
        <BaseInput
          as="textarea" id="content" label="Contenu"
          placeholder="Rédigez votre article ici…" required rows={12}
          value={content} onChange={(e) => setContent(e.target.value)}
        />
        {error && <p style={{ color: '#e53e3e', marginBottom: '0.75rem' }}>{error}</p>}
        <BaseButton type="submit" disabled={busy}>
          {busy ? 'Enregistrement…' : 'Enregistrer'}
        </BaseButton>
      </form>
    </div>
  )
}

export default PostForm
