import { cn } from '@/lib/utils'

export function Skeleton({ className }) {
  return (
    <div
      className={cn('animate-pulse rounded-md bg-slate-200/80', className)}
      aria-hidden
    />
  )
}

export function DashboardTableSkeleton() {
  return (
    <div className="w-full space-y-3 rounded-lg border border-neutral-border bg-white p-4">
      <Skeleton className="h-10 w-full max-w-md" />
      <Skeleton className="h-64 w-full" />
    </div>
  )
}
