import React, { useEffect } from 'react'

/**
 * Modale générique avec overlay.
 * Ferme sur Escape et clic sur l'overlay.
 */
const BaseModal = ({ isOpen, onClose, title, children }) => {
  useEffect(() => {
    if (!isOpen) return
    const onKey = (e) => { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [isOpen, onClose])

  if (!isOpen) return null

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      onClick={onClose}
      style={{
        position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.45)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        zIndex: 1000,
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: '#fff', borderRadius: 10, padding: '1.5rem',
          minWidth: 320, maxWidth: '90vw', boxShadow: '0 8px 32px rgba(0,0,0,0.18)',
        }}
      >
        {title && <h2 id="modal-title" style={{ marginBottom: '1rem' }}>{title}</h2>}
        {children}
      </div>
    </div>
  )
}

export default BaseModal
