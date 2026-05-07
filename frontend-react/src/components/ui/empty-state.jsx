import { cn } from '@/lib/utils'

/**
 * Estado vazio com mensagem orientadora e ação opcional (UX).
 */
export function EmptyState({
  className,
  icon: Icon,
  title,
  description,
  children,
  compact = false,
}) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center text-center',
        compact ? 'py-8 px-4' : 'py-12 px-6',
        className
      )}
      role="status"
      aria-live="polite"
    >
      {Icon && (
        <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-slate-100 text-slate-500">
          <Icon className="h-7 w-7" aria-hidden />
        </div>
      )}
      {title && (
        <h3 className="text-base font-semibold text-gray-900 max-w-md">{title}</h3>
      )}
      {description && (
        <p className="mt-2 text-sm text-gray-600 max-w-md leading-relaxed">{description}</p>
      )}
      {children && <div className="mt-6 flex flex-wrap items-center justify-center gap-2">{children}</div>}
    </div>
  )
}
