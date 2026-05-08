import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import toast from 'react-hot-toast'
import {
  Gavel,
  Lock,
  User,
  Shield,
  LogIn,
  Eye,
  EyeOff,
  CalendarDays,
  FileSpreadsheet,
  History,
  Sparkles,
  CheckCircle2,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { cn } from '@/lib/utils'

const FEATURES = [
  {
    icon: FileSpreadsheet,
    title: 'Importação flexível',
    text: 'Grelha no browser, Excel/CSV ou Google Sheets com monitorização opcional.',
  },
  {
    icon: CalendarDays,
    title: 'Prazos e calendário',
    text: 'Visualize vencimentos e alertas sem perder o contexto operacional.',
  },
  {
    icon: History,
    title: 'Trilho de alterações',
    text: 'Histórico útil para auditoria e rastreio da origem das mudanças.',
  },
]

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      await login(username, password)
      toast.success('Login realizado com sucesso!')
      navigate('/dashboard')
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao fazer login')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#0c1420]">
      {/* Fundo global */}
      <div
        className="pointer-events-none fixed inset-0 opacity-[0.45]"
        aria-hidden
        style={{
          backgroundImage: `
            radial-gradient(ellipse 80% 55% at 20% 15%, rgba(45, 86, 120, 0.45), transparent 55%),
            radial-gradient(ellipse 70% 50% at 85% 75%, rgba(30, 58, 95, 0.35), transparent 50%),
            linear-gradient(180deg, #0c1420 0%, #0f1b28 45%, #0a111a 100%)
          `,
        }}
      />
      <div
        className="pointer-events-none fixed inset-0 opacity-[0.06]"
        style={{
          backgroundImage: `linear-gradient(rgba(255,255,255,0.35) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.35) 1px, transparent 1px)`,
          backgroundSize: '48px 48px',
        }}
        aria-hidden
      />

      <div className="relative z-10 flex min-h-screen flex-col lg:flex-row">
        {/* Painel institucional — desktop */}
        <aside
          className={cn(
            'relative hidden flex-col justify-between overflow-hidden px-10 py-12 text-white lg:flex lg:w-[min(44vw,520px)] xl:px-14 xl:py-16',
            'border-r border-white/[0.08] bg-[#111e2e]/90 backdrop-blur-xl'
          )}
        >
          <div
            className="pointer-events-none absolute inset-0 opacity-[0.12]"
            aria-hidden
            style={{
              backgroundImage:
                'radial-gradient(circle at 30% 20%, rgba(149, 183, 210, 0.5), transparent 42%)',
            }}
          />

          <div className="relative">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/[0.12] ring-1 ring-white/20 shadow-lg shadow-black/20">
                <Gavel className="h-6 w-6 text-[#c8dde9]" strokeWidth={2} aria-hidden />
              </div>
              <div>
                <p className="font-serif text-xl font-bold tracking-tight text-white">Sistema PGR</p>
                <p className="text-xs font-medium uppercase tracking-[0.18em] text-[#8fa9bd]">
                  Processos administrativos
                </p>
              </div>
            </div>

            <h1 className="mt-10 max-w-[22rem] font-serif text-3xl font-bold leading-tight tracking-tight text-white xl:text-[2rem] xl:leading-snug">
              Gestão de processos com clareza e controle do seu escritório.
            </h1>
            <p className="mt-4 max-w-sm text-sm leading-relaxed text-[#b4c5d4]">
              Acompanhe prazos, importações e documentação num só lugar — com dados isolados por conta e apoio a
              fluxos reais de trabalho.
            </p>

            <ul className="mt-10 space-y-5">
              {FEATURES.map(({ icon: Icon, title, text }) => (
                <li key={title} className="flex gap-4">
                  <span className="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#1e3347]/90 ring-1 ring-white/10">
                    <Icon className="h-5 w-5 text-[#a8c4da]" aria-hidden />
                  </span>
                  <div>
                    <p className="flex items-center gap-2 text-sm font-semibold text-white">
                      <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400/90" aria-hidden />
                      {title}
                    </p>
                    <p className="mt-1 text-xs leading-relaxed text-[#9fb2c4]">{text}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          <div className="relative mt-12 flex flex-wrap items-center gap-x-4 gap-y-2 border-t border-white/[0.08] pt-8 text-xs text-[#8fa9bd]">
            <span className="inline-flex items-center gap-1.5 rounded-full bg-white/[0.06] px-3 py-1 ring-1 ring-white/10">
              <Shield className="h-3.5 w-3.5 text-emerald-300/90" aria-hidden />
              Acesso autenticado
            </span>
            <span className="inline-flex items-center gap-1.5 text-[#8fa9bd]/90">
              <Sparkles className="h-3.5 w-3.5 text-amber-200/80" aria-hidden />
              Recomenda-se HTTPS em produção
            </span>
          </div>
        </aside>

        {/* Formulário */}
        <main className="flex flex-1 flex-col items-center justify-center px-4 py-10 sm:px-8 lg:px-12 lg:py-16">
          {/* Cabeçalho mobile */}
          <div className="mb-8 flex items-center gap-3 lg:hidden">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-white/[0.1] ring-1 ring-white/15">
              <Gavel className="h-5 w-5 text-[#c8dde9]" aria-hidden />
            </div>
            <div>
              <p className="font-serif text-lg font-bold text-white">Sistema PGR</p>
              <p className="text-[11px] font-medium uppercase tracking-wider text-[#8fa9bd]">Entrar</p>
            </div>
          </div>

          <div className="w-full max-w-[440px]">
            <Card className="overflow-hidden border border-[#1f2f42]/80 bg-[#fcfcfd]/[0.97] shadow-[0_28px_70px_-34px_rgba(0,0,0,0.65),0_0_0_1px_rgba(255,255,255,0.06)_inset] backdrop-blur-md">
              <div className="h-1 bg-gradient-to-r from-[#2d5678] via-[#4a7eaf] to-[#2d5678]" aria-hidden />

              <CardHeader className="space-y-1 pb-2 pt-8 text-center sm:text-left">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#5c7289]">Área reservada</p>
                <h2 className="font-serif text-2xl font-bold tracking-tight text-[#182534]">Bem-vindo de volta</h2>
                <p className="text-sm leading-relaxed text-[#5c6d80]">
                  Introduza as suas credenciais para aceder ao painel e aos seus processos.
                </p>
              </CardHeader>

              <CardContent className="space-y-6 px-6 pb-8 pt-4 sm:px-8">
                <form className="space-y-5" onSubmit={handleSubmit}>
                  <div className="space-y-2">
                    <Label htmlFor="username" className="text-[13px] font-medium text-[#334155]">
                      Utilizador
                    </Label>
                    <div className="relative">
                      <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5">
                        <User className="h-[18px] w-[18px] text-[#94a3b8]" aria-hidden />
                      </div>
                      <Input
                        id="username"
                        name="username"
                        type="text"
                        required
                        autoComplete="username"
                        className={cn(
                          'h-12 rounded-xl border-[#d4dbe3] bg-white pl-11 text-[15px] text-[#182534]',
                          'shadow-[0_10px_28px_-26px_rgba(15,23,42,0.55)] placeholder:text-[#94a3b8]',
                          'focus-visible:border-[#2d5678] focus-visible:ring-[3px] focus-visible:ring-[#95b7d2]/35'
                        )}
                        placeholder="ex.: admin ou o seu utilizador"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        disabled={loading}
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="password" className="text-[13px] font-medium text-[#334155]">
                      Palavra-passe
                    </Label>
                    <div className="relative">
                      <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5">
                        <Lock className="h-[18px] w-[18px] text-[#94a3b8]" aria-hidden />
                      </div>
                      <Input
                        id="password"
                        name="password"
                        type={showPassword ? 'text' : 'password'}
                        required
                        autoComplete="current-password"
                        className={cn(
                          'h-12 rounded-xl border-[#d4dbe3] bg-white pl-11 pr-11 text-[15px] text-[#182534]',
                          'shadow-[0_10px_28px_-26px_rgba(15,23,42,0.55)] placeholder:text-[#94a3b8]',
                          'focus-visible:border-[#2d5678] focus-visible:ring-[3px] focus-visible:ring-[#95b7d2]/35'
                        )}
                        placeholder="••••••••"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        disabled={loading}
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute inset-y-0 right-0 flex items-center pr-3.5 text-[#94a3b8] transition-colors hover:text-[#475569] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#95b7d2]/50 focus-visible:ring-offset-2 rounded-md"
                        aria-label={showPassword ? 'Ocultar palavra-passe' : 'Mostrar palavra-passe'}
                      >
                        {showPassword ? <EyeOff className="h-5 w-5" aria-hidden /> : <Eye className="h-5 w-5" aria-hidden />}
                      </button>
                    </div>
                  </div>

                  <Button
                    type="submit"
                    disabled={loading}
                    className={cn(
                      'mt-2 h-12 w-full rounded-xl border border-[#1e3347]/20 bg-[#1A2B3C] text-[15px] font-semibold text-white',
                      'shadow-[0_14px_36px_-22px_rgba(26,43,60,0.9)] hover:bg-[#243952]',
                      'focus-visible:ring-2 focus-visible:ring-[#95b7d2]/45 focus-visible:ring-offset-2'
                    )}
                    size="lg"
                  >
                    {loading ? (
                      <>
                        <span
                          className="h-5 w-5 shrink-0 animate-spin rounded-full border-2 border-white border-t-transparent"
                          aria-hidden
                        />
                        <span>A entrar…</span>
                      </>
                    ) : (
                      <>
                        <LogIn className="h-5 w-5" aria-hidden />
                        <span>Entrar</span>
                      </>
                    )}
                  </Button>
                </form>

                <p className="flex items-start gap-2 rounded-xl border border-[#e8ecf2] bg-[#f6f8fb] px-3.5 py-3 text-xs leading-relaxed text-[#5c6d80]">
                  <Shield className="mt-0.5 h-4 w-4 shrink-0 text-[#2d5678]" aria-hidden />
                  <span>
                    As sessões utilizam token seguro. Em ambientes partilhados, termine sempre a sessão ao sair do
                    navegador.
                  </span>
                </p>
              </CardContent>
            </Card>

            <p className="mt-8 text-center text-[13px] text-[#8fa9bd]/95">
              © {new Date().getFullYear()} Sistema PGR · Uso institucional
            </p>
          </div>
        </main>
      </div>
    </div>
  )
}
