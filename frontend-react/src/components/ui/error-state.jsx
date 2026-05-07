import { AlertTriangle } from 'lucide-react'
import { cn } from '@/lib/utils'

export function ErrorState({ title = 'Algo correu mal', description, children, className }) {
  return (
    <div
      className={cn(
        'rounded-lg border border-red-200 bg-red-50/90 px-4 py-5 text-center sm:text-left sm:flex sm:items-start sm:gap-4',
        className
      )}
      role="alert"
    >
      <div className="mx-auto flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-red-100 text-red-700 sm:mx-0">
        <AlertTriangle className="h-5 w-5" aria-hidden />
      </div>
      <div className="mt-3 sm:mt-0 flex-1 min-w-0">
        <h3 className="text-sm font-semibold text-red-900">{title}</h3>
        {description && (
          <p className="mt-1 text-sm text-red-800/90 whitespace-pre-wrap">{description}</p>
        )}
        {children && <div className="mt-4 flex flex-wrap gap-2">{children}</div>}
      </div>
    </div>
  )
}
