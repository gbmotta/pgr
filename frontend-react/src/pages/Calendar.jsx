import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import axios from 'axios'
import {
  format,
  startOfMonth,
  endOfMonth,
  startOfWeek,
  endOfWeek,
  eachDayOfInterval,
  addMonths,
  isSameMonth,
  isToday,
} from 'date-fns'
import { ptBR } from 'date-fns/locale'
import {
  Calendar as CalendarIcon,
  ChevronLeft,
  ChevronRight,
  Clock,
  FileText,
  Loader2,
  Filter,
} from 'lucide-react'
import { API_URL } from '@/lib/apiConfig'

function parseDdMm(prazoFinal) {
  if (!prazoFinal || typeof prazoFinal !== 'string') return null
  const parts = prazoFinal.trim().split('/')
  if (parts.length !== 2) return null
  const day = parseInt(parts[0], 10)
  const month = parseInt(parts[1], 10)
  if (Number.isNaN(day) || Number.isNaN(month) || month < 1 || month > 12) return null
  return { day, month }
}

function processHref(p) {
  const id = p.processo_adm_1doc || p.processo_judicial || p.protocol_number
  if (!id) return null
  return `/process/${encodeURIComponent(id)}`
}

function buildCalendarEvents(processes, overdue, upcoming, year, monthIndex) {
  const map = {}

  const push = (dateKey, item) => {
    if (!map[dateKey]) map[dateKey] = []
    map[dateKey].push(item)
  }

  for (const p of processes || []) {
    if (!p.prazo_final) continue
    const pm = parseDdMm(p.prazo_final)
    if (!pm) continue
    const dt = new Date(year, pm.month - 1, pm.day)
    if (dt.getFullYear() !== year || dt.getMonth() !== monthIndex || dt.getDate() !== pm.day) {
      continue
    }
    const key = format(dt, 'yyyy-MM-dd')
    const label = p.processo_adm_1doc || p.processo_judicial || p.protocol_number || 'Processo'
    push(key, {
      key: `pf-${p.id ?? label}-${key}`,
      kind: 'prazo_final',
      title: label,
      subtitle: 'Prazo final (planilha)',
      href: processHref(p),
    })
  }

  const mergeDeadline = (list, overdueFlag) => {
    for (const d of list || []) {
      const raw = d.due_date
      if (!raw) continue
      const key = String(raw).slice(0, 10)
      if (!/^\d{4}-\d{2}-\d{2}$/.test(key)) continue
      const [y, m] = key.split('-').map(Number)
      if (y !== year || m - 1 !== monthIndex) continue
      const proto = d.protocol_number || ''
      push(key, {
        key: `dl-${key}-${d.deadline_name}-${proto}-${overdueFlag}`,
        kind: overdueFlag ? 'deadline_overdue' : 'deadline',
        title: d.deadline_name || 'Prazo legal',
        subtitle: proto || '—',
        href: proto ? `/process/${encodeURIComponent(proto)}` : null,
      })
    }
  }

  mergeDeadline(overdue, true)
  mergeDeadline(upcoming, false)

  return map
}

const WEEKDAYS = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']

/** @typedef {'all' | 'sheet' | 'legal_upcoming' | 'legal_overdue'} CalendarEventFilter */

export default function Calendar() {
  const [cursor, setCursor] = useState(() => new Date())
  const [selectedKey, setSelectedKey] = useState(null)
  /** @type {[CalendarEventFilter, React.Dispatch<React.SetStateAction<CalendarEventFilter>>]} */
  const [eventFilter, setEventFilter] = useState(() => /** @type {CalendarEventFilter} */ ('all'))

  const { data: processes = [], isLoading: loadingProc } = useQuery({
    queryKey: ['processes'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/processes`)
      return res.data
    },
  })

  const { data: overdue = [], isLoading: loadingOver } = useQuery({
    queryKey: ['deadlines-overdue'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/deadlines/overdue`)
      return res.data
    },
  })

  const { data: upcoming = [], isLoading: loadingUp } = useQuery({
    queryKey: ['deadlines-upcoming-calendar'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/deadlines/upcoming`, { params: { days: 365 } })
      return res.data
    },
  })

  const loading = loadingProc || loadingOver || loadingUp

  const monthStart = startOfMonth(cursor)
  const monthEnd = endOfMonth(cursor)
  const gridStart = startOfWeek(monthStart, { weekStartsOn: 1 })
  const gridEnd = endOfWeek(monthEnd, { weekStartsOn: 1 })
  const days = eachDayOfInterval({ start: gridStart, end: gridEnd })

  const year = cursor.getFullYear()
  const monthIndex = cursor.getMonth()

  const eventsByDay = useMemo(
    () => buildCalendarEvents(processes, overdue, upcoming, year, monthIndex),
    [processes, overdue, upcoming, year, monthIndex]
  )

  const filteredEventsByDay = useMemo(() => {
    if (eventFilter === 'all') return eventsByDay
    const out = {}
    for (const [key, list] of Object.entries(eventsByDay)) {
      const filtered = list.filter((ev) => {
        if (eventFilter === 'sheet') return ev.kind === 'prazo_final'
        if (eventFilter === 'legal_upcoming') return ev.kind === 'deadline'
        if (eventFilter === 'legal_overdue') return ev.kind === 'deadline_overdue'
        return true
      })
      if (filtered.length) out[key] = filtered
    }
    return out
  }, [eventsByDay, eventFilter])

  const selectedEvents = selectedKey ? filteredEventsByDay[selectedKey] || [] : []

  const filterOptions = [
    { id: 'all', label: 'Todos' },
    { id: 'sheet', label: 'Prazo final (planilha)' },
    { id: 'legal_upcoming', label: 'Prazos legais a vencer' },
    { id: 'legal_overdue', label: 'Prazos legais vencidos' },
  ]

  return (
    <div className="space-y-6">
      <section className="surface-panel px-6 py-6 lg:px-8">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <span className="hero-badge">
            <CalendarIcon className="h-3.5 w-3.5" />
            Visão temporal
          </span>
          <h1 className="page-title mt-4 text-3xl md:text-[2.35rem]">Calendário</h1>
          <p className="page-subtitle mt-3">
            Prazos finais dos seus processos e prazos legais (vencidos e próximos 12 meses).
          </p>
        </div>
        <div className="flex items-center gap-2 rounded-2xl border border-[#d8dde4] bg-white/90 p-1.5 shadow-[0_14px_28px_-26px_rgba(15,23,42,0.6)]">
          <button
            type="button"
            onClick={() => setCursor((d) => addMonths(d, -1))}
            className="rounded-xl p-2 text-gray-600 hover:bg-gray-100"
            aria-label="Mês anterior"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          <span className="min-w-[10rem] text-center text-sm font-semibold capitalize text-gray-900">
            {format(cursor, 'MMMM yyyy', { locale: ptBR })}
          </span>
          <button
            type="button"
            onClick={() => setCursor((d) => addMonths(d, 1))}
            className="rounded-xl p-2 text-gray-600 hover:bg-gray-100"
            aria-label="Mês seguinte"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
          <button
            type="button"
            onClick={() => {
              const t = new Date()
              setCursor(t)
              setSelectedKey(format(t, 'yyyy-MM-dd'))
            }}
            className="ml-1 rounded-xl border border-gray-200 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50"
          >
            Hoje
          </button>
        </div>
      </div>
      </section>

      <div className="surface-panel flex flex-wrap items-center gap-2 px-3 py-3">
        <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-600">
          <Filter className="h-4 w-4 text-gray-500" aria-hidden />
          Mostrar:
        </span>
        <div className="flex flex-wrap gap-2" role="group" aria-label="Filtrar tipo de evento no calendário">
          {filterOptions.map((opt) => (
            <button
              key={opt.id}
              type="button"
              onClick={() => setEventFilter(opt.id)}
              className={`rounded-full px-3 py-1 text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 ${
                eventFilter === opt.id
                  ? 'bg-[#1e3347] text-white shadow-sm'
                  : 'bg-[#eef1f5] text-gray-700 hover:bg-[#e3e8ee]'
              }`}
              aria-pressed={eventFilter === opt.id}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      <div className="flex flex-col gap-6 lg:flex-row">
        <div className="surface-panel flex-1 overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center py-24 text-gray-500 gap-2">
              <Loader2 className="h-6 w-6 animate-spin" />
              <span>A carregar prazos…</span>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-7 border-b border-gray-100 bg-[#f6f3ee]">
                {WEEKDAYS.map((w) => (
                  <div
                    key={w}
                    className="px-1 py-2 text-center text-xs font-semibold uppercase tracking-wide text-slate-600"
                  >
                    {w}
                  </div>
                ))}
              </div>
              <div className="grid grid-cols-7">
                {days.map((day) => {
                  const key = format(day, 'yyyy-MM-dd')
                  const inMonth = isSameMonth(day, cursor)
                  const events = filteredEventsByDay[key] || []
                  const isSel = selectedKey === key
                  const today = isToday(day)

                  return (
                    <button
                      key={key}
                      type="button"
                      onClick={() => setSelectedKey(key)}
                      className={[
                        'min-h-[5.5rem] border-b border-r border-gray-100 p-1 text-left transition-colors hover:bg-[#f7f0e6]',
                        !inMonth && 'bg-gray-50/80 text-gray-400',
                        isSel && 'ring-2 ring-inset ring-[#2f5c81] bg-[#eef5fb]',
                        today && !isSel && 'bg-[#fbf1dd]',
                      ]
                        .filter(Boolean)
                        .join(' ')}
                    >
                      <div
                        className={`text-xs font-medium tabular-nums ${
                          today ? 'text-amber-800' : inMonth ? 'text-gray-900' : 'text-gray-400'
                        }`}
                      >
                        {format(day, 'd')}
                      </div>
                      <div className="mt-1 flex flex-wrap gap-0.5">
                        {events.slice(0, 3).map((ev) => (
                          <span
                            key={ev.key}
                            className={[
                              'h-1.5 w-1.5 rounded-full',
                              ev.kind === 'prazo_final' && 'bg-blue-500',
                              ev.kind === 'deadline' && 'bg-amber-500',
                              ev.kind === 'deadline_overdue' && 'bg-red-500',
                            ]
                              .filter(Boolean)
                              .join(' ')}
                            title={ev.title}
                          />
                        ))}
                        {events.length > 3 && (
                          <span className="text-[10px] text-gray-500">+{events.length - 3}</span>
                        )}
                      </div>
                    </button>
                  )
                })}
              </div>
            </>
          )}
        </div>

        <div className="surface-panel w-full shrink-0 p-4 lg:w-80">
          <h2 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
            <CalendarIcon className="h-4 w-4 text-gray-500" />
            {selectedKey
              ? format(new Date(selectedKey + 'T12:00:00'), "d 'de' MMMM", { locale: ptBR })
              : 'Selecione um dia'}
          </h2>
          <div className="mt-3 space-y-2 text-xs text-gray-600">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-blue-500" />
              Prazo final (planilha)
            </div>
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-amber-500" />
              Prazo legal (a vencer)
            </div>
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-red-500" />
              Prazo legal vencido
            </div>
          </div>
          <div className="soft-scrollbar mt-4 max-h-[28rem] space-y-3 overflow-y-auto border-t border-gray-100 pt-4">
            {!selectedKey && (
              <p className="text-sm text-gray-500">Clique num dia na grelha para ver o detalhe.</p>
            )}
            {selectedKey && selectedEvents.length === 0 && (
              <p className="text-sm text-gray-500">
                {eventFilter === 'all'
                  ? 'Sem eventos neste dia.'
                  : 'Sem eventos deste tipo neste dia — altere o filtro ou escolha outra data.'}
              </p>
            )}
            {selectedEvents.map((ev) => (
              <div
                key={ev.key}
                className="rounded-2xl border border-gray-100 bg-[#f8f6f1] px-3 py-2 text-sm"
              >
                <div className="flex items-start gap-2">
                  {ev.kind === 'prazo_final' ? (
                    <FileText className="h-4 w-4 text-blue-600 shrink-0 mt-0.5" />
                  ) : (
                    <Clock
                      className={`h-4 w-4 shrink-0 mt-0.5 ${
                        ev.kind === 'deadline_overdue' ? 'text-red-600' : 'text-amber-600'
                      }`}
                    />
                  )}
                  <div className="min-w-0 flex-1">
                    <p className="font-medium text-gray-900 truncate" title={ev.title}>
                      {ev.title}
                    </p>
                    <p className="text-xs text-gray-600">{ev.subtitle}</p>
                    {ev.href && (
                      <Link
                        to={ev.href}
                        className="mt-1 inline-block text-xs font-medium text-blue-600 hover:underline"
                      >
                        Abrir processo
                      </Link>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
