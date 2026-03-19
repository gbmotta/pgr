import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { 
  LayoutDashboard, 
  Upload, 
  FileText, 
  LogOut,
  Gavel,
  Menu,
  X,
  Bell,
  TrendingUp
} from 'lucide-react'
import { useState } from 'react'

export default function InstitutionalLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const navItems = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/upload', icon: Upload, label: 'Upload' },
    { to: '/reports', icon: FileText, label: 'Relatórios' },
    { to: '/performance', icon: TrendingUp, label: 'Performance' },
  ]

  const isActive = (path) => {
    // Rota raiz ou dashboard
    if (path === '/dashboard') {
      return location.pathname === '/dashboard' || location.pathname === '/'
    }
    // Para outras rotas, verificar match exato
    return location.pathname === path
  }

  return (
    <div className="h-screen flex flex-col bg-[#fafafa] overflow-hidden">
      {/* Topbar */}
      <header className="h-14 bg-[#1a1a2e] border-b border-[#e0e0e0] flex-shrink-0 z-50">
        <div className="h-full px-6 flex items-center justify-between">
          {/* Logo/Identificação */}
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded transition-colors"
              aria-label="Toggle sidebar"
            >
              {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
            <div className="flex items-center space-x-3">
              <div className="bg-white/10 p-2 rounded">
                <Gavel className="h-5 w-5 text-white" />
              </div>
              <div>
                <h1 className="text-base font-semibold text-white">Sistema PGR</h1>
                <p className="text-xs text-white/70">Controle de Processos Administrativos</p>
              </div>
            </div>
          </div>

          {/* Direita: Usuário + Notificações + Logout */}
          <div className="flex items-center space-x-4">
            <button className="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded transition-colors relative">
              <Bell className="h-5 w-5" />
              <span className="absolute top-1 right-1 h-2 w-2 bg-[#c0392b] rounded-full"></span>
            </button>
            <div className="h-8 w-px bg-white/20"></div>
            <span className="text-sm text-white/90 font-medium">
              {user?.full_name || user?.username}
            </span>
            <button
              onClick={handleLogout}
              className="inline-flex items-center px-3 py-1.5 text-sm font-medium rounded text-white hover:bg-white/10 transition-colors"
            >
              <LogOut className="mr-2 h-4 w-4" />
              Sair
            </button>
          </div>
        </div>
      </header>

      {/* Container Principal: Sidebar + Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside
          className={`
            bg-white border-r border-[#e0e0e0] flex-shrink-0 transition-all duration-300
            ${sidebarOpen ? 'w-[260px]' : 'w-16'}
          `}
        >
          <nav className="h-full py-4">
            {navItems.map((item) => {
              const Icon = item.icon
              const active = isActive(item.to)
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className={`
                    flex items-center px-4 py-3 mx-2 mb-1 rounded transition-all
                    ${active
                      ? 'bg-[#f5f5f5] text-[#1a1a2e] font-semibold border-l-3 border-[#1a1a2e]'
                      : 'text-[#616161] hover:bg-[#f5f5f5] hover:text-[#1a1a2e]'
                    }
                  `}
                  style={active ? { borderLeftWidth: '3px' } : {}}
                >
                  <Icon className={`h-5 w-5 flex-shrink-0 ${active ? 'text-[#1a1a2e]' : 'text-[#616161]'}`} />
                  {sidebarOpen && (
                    <span className={`ml-3 text-sm ${active ? 'font-semibold' : 'font-medium'}`}>
                      {item.label}
                    </span>
                  )}
                </Link>
              )
            })}
          </nav>
        </aside>

        {/* Content Area */}
        <main
          className={`
            flex-1 overflow-auto bg-[#fafafa]
            transition-all duration-300
          `}
        >
          <div className="p-6">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
