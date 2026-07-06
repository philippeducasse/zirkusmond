import { useEffect, useRef, useState } from 'react'
import { useRouterState } from '@tanstack/react-router'

const SCROLL_THRESHOLD = 100

/**
 * Mirrors the legacy Django navbar: solid everywhere except the homepage,
 * where it stays transparent until scrolled past SCROLL_THRESHOLD.
 * Uses an IntersectionObserver against a sentinel instead of a scroll listener.
 */
export function useStickyNavbar() {
  const isHome = useRouterState({ select: (state) => state.location.pathname === '/' })
  const [sticky, setSticky] = useState(!isHome)
  const sentinelRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!isHome) {
      setSticky(true)
      return
    }

    const sentinel = sentinelRef.current
    if (!sentinel) return

    const observer = new IntersectionObserver(([entry]) => setSticky(!entry.isIntersecting))
    observer.observe(sentinel)
    return () => observer.disconnect()
  }, [isHome])

  return { sticky, sentinelRef, scrollThreshold: SCROLL_THRESHOLD }
}