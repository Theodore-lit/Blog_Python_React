import React from 'react'

/**
 * Bouton générique réutilisable.
 * variant : 'primary' | 'danger' | 'ghost'
 */
const STYLES = {
  base: {
    border: 'none', borderRadius: 6, padding: '0.5rem 1.1rem',
    fontWeight: 600, fontSize: '0.9rem', cursor: 'pointer',
    transition: 'opacity 0.15s',
  },
  primary: { background: '#3182ce', color: '#fff' },
  danger:  { background: '#e53e3e', color: '#fff' },
  ghost:   { background: '#eee',    color: '#333' },
}

const BaseButton = ({
  children,
  variant = 'primary',
  disabled = false,
  type = 'button',
  onClick,
  style = {},
}) => (
  <button
    type={type}
    disabled={disabled}
    onClick={onClick}
    style={{
      ...STYLES.base,
      ...STYLES[variant] ?? STYLES.primary,
      opacity: disabled ? 0.55 : 1,
      ...style,
    }}
  >
    {children}
  </button>
)

export default BaseButton
