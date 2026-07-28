import { useEffect, useState, type ReactNode } from 'react'
import { cn } from '#/lib/utils.ts'

interface CrossFadeProps {
  isLoading: boolean
  skeleton: ReactNode
  children: ReactNode
  duration?: number
}

const CrossFade = ({
  isLoading,
  skeleton,
  children,
  duration = 300,
}: CrossFadeProps) => {
  const [showSkeleton, setShowSkeleton] = useState(isLoading)

  useEffect(() => {
    if (isLoading) {
      setShowSkeleton(true)
      return
    }
    const timer = setTimeout(() => setShowSkeleton(false), duration)
    return () => clearTimeout(timer)
  }, [isLoading, duration])

  return (
    <div className="grid [&>*]:col-start-1 [&>*]:row-start-1">
      {showSkeleton && (
        <div
          className={cn(
            'transition-opacity',
            isLoading ? 'opacity-100' : 'opacity-0',
          )}
          style={{ transitionDuration: `${duration}ms` }}
        >
          {skeleton}
        </div>
      )}
      {!isLoading && (
        <div
          className="animate-in fade-in"
          style={{ animationDuration: `${duration}ms` }}
        >
          {children}
        </div>
      )}
    </div>
  )
}

export default CrossFade