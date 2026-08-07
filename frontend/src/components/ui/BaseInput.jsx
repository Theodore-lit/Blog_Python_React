import React from 'react'

/**
 * Champ de saisie générique.
 * Supporte type text, email, password, textarea (via as='textarea').
 */
const FIELD_STYLE = {
  display: 'block',
  width: '100%',
  padding: '0.5rem 0.75rem',
  border: '1px solid #ccc',
  borderRadius: 6,
  fontSize: '0.95rem',
  marginBottom: '0.75rem',
  fontFamily: 'inherit',
  boxSizing: 'border-box',
}

const BaseInput = ({
  as = 'input',
  label,
  id,
  error,
  style = {},
  ...props
}) => {
  const Field = as
  return (
    <div>
      {label && (
        <label htmlFor={id} style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 500 }}>
          {label}
        </label>
      )}
      <Field
        id={id}
        style={{ ...FIELD_STYLE, borderColor: error ? '#e53e3e' : '#ccc', ...style }}
        {...props}
      />
      {error && <p style={{ color: '#e53e3e', fontSize: '0.8rem', marginTop: '-0.5rem', marginBottom: '0.5rem' }}>{error}</p>}
    </div>
  )
}

export default BaseInput
