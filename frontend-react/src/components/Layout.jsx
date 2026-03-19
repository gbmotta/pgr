import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { 
  LayoutDashboard, 
  Upload, 
  FileText, 
  LogOut,
  Gavel
} from 'lucide-react'

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const navItems = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/upload', icon: Upload, label: 'Upload' },
    { to: '/reports', icon: FileText, label: 'Relatórios' },
  ]

  const isActive = (path) => {
    if (path === '/dashboard') {
      return location.pathname === '/dashboard' || location.pathname === '/'
    }
    return location.pathname === path
  }

  return (
    <div className="h-screen flex flex-col bg-slate-50 overflow-hidden">
      {/* Cabeçalho fixo com abas */}
      <header className="bg-white border-b-2 border-blue-900 shadow-lg flex-shrink-0">
        {/* Barra superior com logo e usuário */}
        <div className="bg-gradient-to-r from-blue-900 to-blue-800 px-6 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-white/10 p-2 rounded-lg">
                <Gavel className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white font-serif">Sistema PGR</h1>
                <p className="text-xs text-blue-100">Controle de Processos</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-white/90 font-medium">
                {user?.full_name || user?.username}
              </span>
              <button
                onClick={handleLogout}
                className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-md text-white bg-red-600/90 hover:bg-red-700 transition-colors"
              >
                <LogOut className="mr-2 h-4 w-4" />
                Sair
              </button>
            </div>
          </div>
        </div>

        {/* Abas de navegação */}
        <nav className="bg-white border-b border-gray-200">
          <div className="flex space-x-1 px-4">
            {navItems.map((item) => {
              const Icon = item.icon
              const active = isActive(item.to)
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className={`
                    inline-flex items-center px-6 py-4 text-sm font-semibold transition-all
                    relative border-b-2
                    ${active
                      ? 'text-blue-900 border-blue-900 bg-blue-50/50'
                      : 'text-gray-600 border-transparent hover:text-blue-700 hover:bg-blue-50/30'
                    }
                  `}
                  style={{
                    marginBottom: active ? '-2px' : '0px'
                  }}
                >
                  <Icon className={`mr-2 h-5 w-5 ${active ? 'text-blue-900' : 'text-gray-500'}`} />
                  {item.label}
                </Link>
              )
            })}
          </div>
        </nav>
      </header>

      {/* Conteúdo principal - tela cheia */}
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}
