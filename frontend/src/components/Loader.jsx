export function Spinner({ size = 18, className = "" }) {
  return (
    <svg
      className={`animate-spin ${className}`}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
    >
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2.5" opacity="0.2" />
      <path d="M21 12a9 9 0 0 0-9-9" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
    </svg>
  );
}

export function PageLoader({ label = "Loading…" }) {
  return (
    <div className="flex items-center justify-center py-24 text-parchment-muted gap-3">
      <Spinner />
      <span className="text-sm">{label}</span>
    </div>
  );
}

export function CardSkeleton() {
  return (
    <div className="card p-5 space-y-4 animate-pulse">
      <div className="h-5 w-24 rounded-full bg-ink-700" />
      <div className="h-5 w-3/4 rounded bg-ink-700" />
      <div className="h-4 w-1/2 rounded bg-ink-700" />
      <div className="flex gap-2">
        <div className="h-5 w-14 rounded-full bg-ink-700" />
        <div className="h-5 w-14 rounded-full bg-ink-700" />
      </div>
    </div>
  );
}
