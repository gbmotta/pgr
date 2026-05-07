import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import {
  LayoutDashboard,
  Upload,
  FileText,
  Calendar,
  Settings,
  LogOut,
  Menu,
  X,
  BarChart3,
  Link2,
  Search,
  Database,
  Wrench,
  UserCircle,
  ChevronRight,
  BellRing,
  ShieldCheck,
} from 'lucide-react'
import { API_URL } from '@/lib/apiConfig'

function NavBadge({ count }) {
  if (count == null || count < 1) return null
  const label = count > 99 ? '99+' : String(count)
  return (
    <span className="ml-auto inline-flex min-w-[1.25rem] justify-center rounded-full bg-amber-500 px-1.5 py-0.5 text-[10px] font-bold leading-none text-[#1A2B3C]">
      {label}
    </span>
  )
}

export default function MainLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [isMobile, setIsMobile] = useState(false)
  const [globalSearch, setGlobalSearch] = useState('')

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768)
      if (window.innerWidth < 768) {
        setSidebarOpen(false)
      }
    }

    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  const { data: stats } = useQuery({
    queryKey: ['statistics'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/statistics/summary`)
      return res.data
    },
  })

  const { data: linkedSheets = [] } = useQuery({
    queryKey: ['linked-sheets-nav'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/sheets/linked`)
      return res.data
    },
  })

  const overdueLegal = stats?.overdue_deadlines ?? 0
  const totalProcesses = stats?.total_processes ?? 0

  const navSections = [
    {
      key: 'overview',
      title: 'Visão geral',
      icon: LayoutDashboard,
      items: [
        { to: '/dashboard', icon: LayoutDashboard, label: 'Painel de processos', badge: null },
        { to: '/performance', icon: BarChart3, label: 'Performance', badge: null },
      ],
    },
    {
      key: 'data',
      title: 'Dados',
      icon: Database,
      items: [
        { to: '/upload', icon: Upload, label: 'Importar dados', badge: null },
        {
          to: '/linked-sheets',
          icon: Link2,
          label: 'Planilhas monitoradas',
          badge: linkedSheets.length > 0 ? linkedSheets.length : null,
        },
      ],
    },
    {
      key: 'tools',
      title: 'Ferramentas',
      icon: Wrench,
      items: [
        { to: '/reports', icon: FileText, label: 'Relatórios', badge: overdueLegal },
        { to: '/calendar', icon: Calendar, label: 'Calendário', badge: overdueLegal },
      ],
    },
    {
      key: 'account',
      title: 'Conta',
      icon: UserCircle,
      items: [{ to: '/settings', icon: Settings, label: 'Configurações', badge: null }],
    },
  ]

  const flatNavItems = navSections.flatMap((s) => s.items)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const isActive = (path) => {
    if (path === '/dashboard') {
      return location.pathname === '/dashboard' || location.pathname === '/'
    }
    return location.pathname === path || location.pathname.startsWith(`${path}/`)
  }

  const getPageTitle = () => {
    const currentItem = flatNavItems.find((item) => isActive(item.to))
    if (currentItem) return currentItem.label

    if (location.pathname.startsWith('/process/')) return 'Detalhes do processo'
    return 'Sistema PGR'
  }

  const breadcrumbItems = (() => {
    const currentItem = flatNavItems.find((item) => isActive(item.to))
    if (location.pathname.startsWith('/process/')) {
      return ['Processos', 'Detalhes']
    }
    if (!currentItem) return ['Painel']
    const parent = navSections.find((section) =>
      section.items.some((item) => item.to === currentItem.to)
    )
    return parent ? [parent.title, currentItem.label] : [currentItem.label]
  })()

  const todayLabel = new Intl.DateTimeFormat('pt-BR', {
    weekday: 'long',
    day: '2-digit',
    month: 'long',
  }).format(new Date())

  const submitGlobalSearch = (e) => {
    e.preventDefault()
    const q = globalSearch.trim()
    if (!q) return
    navigate(`/dashboard?q=${encodeURIComponent(q)}`)
    if (isMobile) setSidebarOpen(false)
  }

  return (
    <div className="flex min-h-screen overflow-hidden bg-transparent text-[#1b2838]">
      {isMobile && sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-[#09121d]/50 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      <aside
        className={`
          fixed inset-y-0 left-0 z-50
          lg:static
          border-r border-white/10 bg-[linear-gradient(180deg,#162536_0%,#1c3044_55%,#182534_100%)] text-white shadow-2xl
          transition-all duration-300 ease-in-out
          w-64
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
          ${sidebarOpen ? '' : 'lg:w-20 lg:max-w-[5rem] overflow-hidden'}
          flex flex-col
        `}
        aria-label="Menu principal"
      >
        <div className="border-b border-white/10 px-4 py-5">
          <div className="flex items-center justify-between gap-3">
            {sidebarOpen && (
              <div className="min-w-0">
                <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-white/55">
                  Painel Jurídico
                </p>
                <h2 className="truncate font-serif text-2xl font-semibold text-white">Sistema PGR</h2>
              </div>
            )}
          <button
            type="button"
            onClick={() => setSidebarOpen(!sidebarOpen)}
              className="rounded-xl p-2 text-white/80 transition-colors hover:bg-white/10 hover:text-white lg:hidden"
            aria-label={sidebarOpen ? 'Fechar menu' : 'Abrir menu'}
          >
            <X className="h-5 w-5" />
          </button>
          </div>
          {sidebarOpen && (
            <div className="mt-4 rounded-2xl border border-white/10 bg-white/5 px-3 py-3 text-sm text-white/75">
              <div className="flex items-center justify-between">
                <span className="text-white/60">Processos ativos</span>
                <span className="font-semibold text-white">{totalProcesses}</span>
              </div>
              <div className="mt-2 flex items-center justify-between">
                <span className="text-white/60">Prazos críticos</span>
                <span className="font-semibold text-amber-300">{overdueLegal}</span>
              </div>
            </div>
          )}
        </div>

        <nav className="soft-scrollbar flex-1 overflow-y-auto py-5" role="navigation">
          {navSections.map((section) => (
            <div key={section.key} className="mb-5">
              {sidebarOpen && (
                <div className="flex items-center gap-2 px-4 pb-2 text-[10px] font-semibold uppercase tracking-[0.24em] text-white/45">
                  <section.icon className="h-3.5 w-3.5 opacity-70" aria-hidden />
                  {section.title}
                </div>
              )}
              {section.items.map((item) => {
                const Icon = item.icon
                const active = isActive(item.to)
                return (
                  <Link
                    key={item.to}
                    to={item.to}
                    onClick={() => isMobile && setSidebarOpen(false)}
                    className={`
                      mx-2 mb-1 flex items-center gap-2 rounded-2xl px-4 py-3 transition-all
                      ${active
                        ? 'bg-[linear-gradient(135deg,rgba(255,255,255,0.18),rgba(255,255,255,0.08))] text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.15),0_10px_24px_-18px_rgba(0,0,0,0.7)]'
                        : 'text-white/78 hover:bg-white/10 hover:text-white'
                      }
                    `}
                    title={!sidebarOpen ? item.label : undefined}
                  >
                    <Icon className={`h-5 w-5 flex-shrink-0 ${active ? 'text-amber-200' : 'text-white/70'}`} />
                    {sidebarOpen && (
                      <>
                        <span className={`flex-1 text-left text-sm font-medium ${active ? 'font-semibold' : ''}`}>
                          {item.label}
                        </span>
                        <NavBadge count={item.badge} />
                      </>
                    )}
                  </Link>
                )
              })}
            </div>
          ))}
        </nav>

        <div className="border-t border-white/10 p-4">
          <div className="flex items-center mb-3 px-2">
            <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-2xl bg-white/15">
              <span className="text-xs font-semibold text-white">
                {(user?.full_name || user?.username || 'U')[0].toUpperCase()}
              </span>
            </div>
            {sidebarOpen && (
              <div className="ml-3 flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  {user?.full_name || user?.username || 'Usuário'}
                </p>
                <p className="text-xs text-white/60 truncate">{user?.email || ''}</p>
              </div>
            )}
          </div>
          <button
            type="button"
            onClick={handleLogout}
            className="flex w-full items-center rounded-2xl px-4 py-3 text-sm font-medium text-white/80 transition-colors hover:bg-white/10 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70"
            title={!sidebarOpen ? 'Sair' : undefined}
          >
            <LogOut className="h-5 w-5 flex-shrink-0" />
            {sidebarOpen && <span className="ml-3">Sair</span>}
          </button>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <header className="z-30 flex-shrink-0 border-b border-[#d8dde5] bg-[#f8f6f1]/92 backdrop-blur-sm">
          <div className="flex min-h-16 flex-col gap-4 px-4 py-4 lg:px-6">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div className="min-w-0">
                <div className="mb-2 flex flex-wrap items-center gap-2 text-xs font-medium text-[#6a7686]">
                  {breadcrumbItems.map((item, idx) => (
                    <span key={`${item}-${idx}`} className="inline-flex items-center gap-2">
                      {idx > 0 && <ChevronRight className="h-3.5 w-3.5 text-[#95a1b1]" aria-hidden />}
                      <span>{item}</span>
                    </span>
                  ))}
                </div>
                <div className="flex items-center gap-3 min-w-0">
              <button
                type="button"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                    className="hidden rounded-xl border border-[#d5dbe4] bg-white/85 p-2 text-[#586576] transition-colors hover:text-[#1d2e40] lg:inline-flex"
                aria-label={sidebarOpen ? 'Colapsar menu lateral' : 'Expandir menu lateral'}
                aria-expanded={sidebarOpen}
              >
                <Menu className="h-6 w-6" />
              </button>
              <button
                type="button"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                    className="rounded-xl border border-[#d5dbe4] bg-white/85 p-2 text-[#586576] transition-colors hover:text-[#1d2e40] lg:hidden"
                aria-label="Abrir menu"
              >
                <Menu className="h-6 w-6" />
              </button>

                  <div className="min-w-0">
              <h1 className="truncate font-serif text-2xl font-semibold text-[#182534] sm:text-[2rem]">
                {getPageTitle()}
              </h1>
                    <p className="mt-1 text-sm text-[#66717f] capitalize">{todayLabel}</p>
                  </div>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                <span className="filter-chip">
                  <ShieldCheck className="h-4 w-4 text-emerald-700" />
                  Conta isolada
                </span>
                <span className="filter-chip">
                  <BellRing className="h-4 w-4 text-amber-700" />
                  {overdueLegal} alerta(s)
                </span>
                <span className="filter-chip">
                  <FileText className="h-4 w-4 text-[#1e3347]" />
                  {totalProcesses} processos
                </span>
              </div>
            </div>

            <form
              onSubmit={submitGlobalSearch}
              className="flex w-full gap-2 sm:max-w-xl"
              role="search"
              aria-label="Pesquisar processos"
            >
              <label htmlFor="global-search" className="sr-only">
                Pesquisar nos seus processos
              </label>
              <div className="relative flex-1">
                <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-[#7b8795]" aria-hidden />
                <input
                  id="global-search"
                  type="search"
                  value={globalSearch}
                  onChange={(e) => setGlobalSearch(e.target.value)}
                  placeholder="Pesquisar processos…"
                  className="h-11 w-full rounded-2xl border border-[#d4dbe3] bg-white/92 py-2 pl-11 pr-3 text-sm text-[#182534] placeholder:text-[#7b8795] shadow-[0_10px_24px_-22px_rgba(15,23,42,0.45)] focus:border-[#2d5678] focus:bg-white focus:outline-none focus:ring-4 focus:ring-[#95b7d2]/25"
                  autoComplete="off"
                />
              </div>
              <button
                type="submit"
                className="shrink-0 rounded-2xl bg-[#1d3348] px-5 py-2 text-sm font-medium text-white shadow-[0_14px_24px_-18px_rgba(15,23,42,0.7)] transition hover:-translate-y-0.5 hover:bg-[#243c53] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2d5678] focus-visible:ring-offset-2"
              >
                Ir
              </button>
            </form>
          </div>
        </header>

        <main id="main-content" className="soft-scrollbar flex-1 overflow-auto bg-transparent" tabIndex={-1}>
          <div className="p-4 lg:p-6">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
