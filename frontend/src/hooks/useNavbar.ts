import { useEffect, useRef, useState } from 'react'
import { useRouterState } from '@tanstack/react-router'

const SCROLL_THRESHOLD = 100

export function useNavbar() {
  const isHome = useRouterState({
    select: (state) => state.location?.pathname === '/',
  })
  const [fixed, setFixed] = useState(!isHome)
  const sentinelRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    console.log('useNavbar effect:', { isHome, fixed })
    if (!isHome) {
      setFixed(true)
      return
    }

    const sentinel = sentinelRef.current
    console.log('sentinel:', sentinel)
    if (!sentinel) return

    const observer = new IntersectionObserver(([entry]) => {
      console.log('intersection:', { isIntersecting: entry.isIntersecting })
      setFixed(!entry.isIntersecting)
    })
    observer.observe(sentinel)
    return () => observer.disconnect()
  }, [isHome])

  return { fixed, sentinelRef, scrollThreshold: SCROLL_THRESHOLD }
}
