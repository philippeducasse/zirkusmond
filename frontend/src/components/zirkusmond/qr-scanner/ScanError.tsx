interface ScanErrorProps {
  error: string
}

export function ScanError({ error }: ScanErrorProps) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
      <div className="flex flex-col items-center justify-center">
        <svg
          className="w-28 h-28 mx-8 text-red-500 mb-4"
          fill="none"
          stroke="currentColor"
          strokeWidth="3"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
        <p className="text-red-800 text-6xl">{error}</p>
      </div>
    </div>
  )
}