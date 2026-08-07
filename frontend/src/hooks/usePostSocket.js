import { useEffect, useRef } from 'react'
import tokenService from '../services/token.service.js'

const WS_BASE    = import.meta.env.VITE_WS_URL
const BACKOFF    = [2000, 4000, 8000, 16000]   // ms — plafonné au dernier palier
const MAX_RETRY  = BACKOFF.length - 1

/**
 * Ouvre une connexion WebSocket sur /api/ws/posts/{postId}?token=...
 * au montage et la ferme proprement au démontage.
 *
 * Les événements reçus sont routés vers les callbacks des hooks enfants
 * via les refs commentRef et likeRef transmises par PostDetail.
 *
 * Reconnexion automatique avec backoff exponentiel (2s→4s→8s→16s)
 * en cas de fermeture inattendue.
 */
const usePostSocket = (postId, commentRef, likeRef) => {
  const retryCount = useRef(0)
  const timerRef   = useRef(null)
  const wsRef      = useRef(null)

  useEffect(() => {
    const token = tokenService.getToken()
    if (!postId || !token) return

    const connect = () => {
      const ws = new WebSocket(`${WS_BASE}/posts/${postId}?token=${token}`)
      wsRef.current = ws

      ws.onopen = () => { retryCount.current = 0 }

      ws.onmessage = ({ data }) => {
        let event
        try { event = JSON.parse(data) } catch { return }

        // Route l'événement vers le hook concerné via les refs
        if (event.type?.startsWith('comment.') && commentRef?.current) {
          commentRef.current(event)
        }
        if (event.type?.startsWith('like.') && likeRef?.current) {
          likeRef.current(event)
        }
      }

      ws.onclose = ({ code }) => {
        // 1000 = fermeture normale (démontage) — pas de reconnexion
        if (code === 1000) return
        const delay = BACKOFF[Math.min(retryCount.current, MAX_RETRY)]
        retryCount.current += 1
        timerRef.current = setTimeout(connect, delay)
      }
    }

    connect()

    return () => {
      clearTimeout(timerRef.current)
      // Code 1000 = fermeture volontaire — empêche la reconnexion dans onclose
      wsRef.current?.close(1000)
    }
  }, [postId, commentRef, likeRef])
}

export default usePostSocket
