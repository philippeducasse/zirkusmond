import { useEffect, useRef, useState } from 'react'
import { useRouterState } from '@tanstack/react-router'

const SCROLL_THRESHOLD = 100

/**
 * Mirrors the legacy Django navbar: solid everywhere except the homepage,
 * where it stays transparent until scrolled past SCROLL_THRESHOLD.
 * Uses an IntersectionObserver against a sentinel instead of a scroll listener.
 */
export function useNavbar() {
  const isHome = useRouterState({
    select: (state) => state.location.pathname === '/',
  })
  const [fixed, setFixed] = useState(!isHome)
  const sentinelRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!isHome) {
      setFixed(true)
      return
    }

    const sentinel = sentinelRef.current
    if (!sentinel) return

    const observer = new IntersectionObserver(([entry]) =>
      setFixed(!entry.isIntersecting),
    )
    observer.observe(sentinel)
    return () => observer.disconnect()
  }, [isHome])

  return { fixed, sentinelRef, scrollThreshold: SCROLL_THRESHOLD }
}
