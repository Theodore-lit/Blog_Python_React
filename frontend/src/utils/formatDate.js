// Formate une date ISO en chaîne lisible selon la locale fr-FR.
// Utilisé dans PostCard et CommentItem.

const DATE_FORMAT = new Intl.DateTimeFormat('fr-FR', {
  day: '2-digit',
  month: 'short',
  year: 'numeric',
})

const DATETIME_FORMAT = new Intl.DateTimeFormat('fr-FR', {
  day: '2-digit',
  month: 'short',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
})

/**
 * Formate une date ISO en "12 août 2026".
 * @param {string} isoString
 * @returns {string}
 */
export const formatDate = (isoString) =>
  DATE_FORMAT.format(new Date(isoString))

/**
 * Formate une date ISO en "12 août 2026 à 10:30".
 * @param {string} isoString
 * @returns {string}
 */
export const formatDateTime = (isoString) =>
  DATETIME_FORMAT.format(new Date(isoString))
