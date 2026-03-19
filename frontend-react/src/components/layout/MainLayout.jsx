import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useState, useEffect } from 'react'
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
  Link2
} from 'lucide-react'

export default function MainLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [isMobile, setIsMobile] = useState(false)

  // Detectar tamanho da tela para responsividade
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

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const navItems = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/performance', icon: BarChart3, label: 'Performance' },
    { to: '/upload', icon: Upload, label: 'Upload' },
    { to: '/linked-sheets', icon: Link2, label: 'Planilhas Monitoradas' },
    { to: '/reports', icon: FileText, label: 'Relatórios' },
    { to: '/calendar', icon: Calendar, label: 'Calendário' },
    { to: '/settings', icon: Settings, label: 'Configurações' },
  ]

  const isActive = (path) => {
    if (path === '/dashboard') {
      return location.pathname === '/dashboard' || location.pathname === '/'
    }
    if (path === '/performance') {
      return location.pathname === '/performance'
    }
    return location.pathname === path
  }

  // Função para obter o título da página atual
  const getPageTitle = () => {
    const currentItem = navItems.find(item => isActive(item.to))
    if (currentItem) return currentItem.label
    
    // Títulos customizados para outras rotas
    if (location.pathname.startsWith('/process/')) return 'Detalhes do Processo'
    if (location.pathname === '/performance') return 'Dashboard de Performance'
    if (location.pathname === '/linked-sheets') return 'Planilhas Monitoradas'
    return 'Sistema PGR'
  }

  return (
    <div className="h-screen flex overflow-hidden bg-[#F9F9F9]">
      {/* Overlay para mobile quando sidebar está aberta */}
      {isMobile && sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar fixa na esquerda com Navy Blue */}
      <aside
        className={`
          fixed lg:static inset-y-0 left-0 z-50
          bg-[#1A2B3C] text-white
          transition-transform duration-300 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
          ${sidebarOpen ? 'w-64' : 'w-0 lg:w-20'}
          flex flex-col
        `}
      >
        {/* Logo/Título do sistema na sidebar */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-white/10">
          {sidebarOpen && (
            <h2 className="text-xl font-serif font-bold text-white">
              Sistema PGR
            </h2>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden p-2 text-white/80 hover:text-white hover:bg-white/10 rounded transition-colors"
            aria-label="Toggle sidebar"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navegação */}
        <nav className="flex-1 py-4 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon
            const active = isActive(item.to)
            return (
              <Link
                key={item.to}
                to={item.to}
                onClick={() => isMobile && setSidebarOpen(false)}
                className={`
                  flex items-center px-4 py-3 mx-2 mb-1 rounded-lg transition-all
                  ${active
                    ? 'bg-white/20 text-white shadow-lg'
                    : 'text-white/80 hover:bg-white/10 hover:text-white'
                  }
                `}
                title={!sidebarOpen ? item.label : ''}
              >
                <Icon className={`h-5 w-5 flex-shrink-0 ${active ? 'text-white' : 'text-white/80'}`} />
                {sidebarOpen && (
                  <span className={`ml-3 text-sm font-medium ${active ? 'font-semibold' : ''}`}>
                    {item.label}
                  </span>
                )}
              </Link>
            )
          })}
        </nav>

        {/* Footer da sidebar com logout */}
        <div className="border-t border-white/10 p-4">
          <div className="flex items-center mb-3 px-2">
            <div className="h-8 w-8 rounded-full bg-white/20 flex items-center justify-center flex-shrink-0">
              <span className="text-xs font-semibold text-white">
                {(user?.full_name || user?.username || 'U')[0].toUpperCase()}
              </span>
            </div>
            {sidebarOpen && (
              <div className="ml-3 flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  {user?.full_name || user?.username || 'Usuário'}
                </p>
                <p className="text-xs text-white/60 truncate">
                  {user?.email || ''}
                </p>
              </div>
            )}
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center px-4 py-2 text-sm font-medium rounded-lg text-white/80 hover:bg-white/10 hover:text-white transition-colors"
            title={!sidebarOpen ? 'Sair' : ''}
          >
            <LogOut className="h-5 w-5 flex-shrink-0" />
            {sidebarOpen && <span className="ml-3">Sair</span>}
          </button>
        </div>
      </aside>

      {/* Conteúdo principal */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Cabeçalho branco no topo */}
        <header className="bg-white border-b border-gray-200 flex-shrink-0 z-30">
          <div className="h-16 px-4 lg:px-6 flex items-center justify-between">
            {/* Botão menu mobile */}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded transition-colors"
              aria-label="Toggle sidebar"
            >
              <Menu className="h-6 w-6" />
            </button>

            {/* Título da página em fonte Serif */}
            <h1 className="text-2xl font-serif font-bold text-gray-900">
              {getPageTitle()}
            </h1>

            {/* Espaço vazio para alinhamento */}
            <div className="w-10 lg:hidden" />
          </div>
        </header>

        {/* Área de conteúdo principal com fundo cinza claro */}
        <main className="flex-1 overflow-auto bg-[#F9F9F9]">
          <div className="p-4 lg:p-6">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
