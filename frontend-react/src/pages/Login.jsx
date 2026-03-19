import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import toast from 'react-hot-toast'
import { Gavel, Lock, User, Shield, LogIn, Eye, EyeOff } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'

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
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#1A2B3C] via-[#2D3436] to-[#1A2B3C] py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Efeitos de fundo decorativos */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-600/20 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-slate-600/20 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-2000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-indigo-600/20 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      <div className="relative max-w-md w-full z-10">
        <Card className="backdrop-blur-sm bg-white/95 border-white/20 shadow-2xl">
          {/* Header do card */}
          <CardHeader className="bg-gradient-to-r from-[#1A2B3C] to-[#2D3436] text-white text-center pb-8">
            <div className="flex justify-center mb-4">
              <div className="bg-white/20 p-4 rounded-xl backdrop-blur-sm">
                <Gavel className="h-10 w-10 text-white" strokeWidth={2} />
              </div>
            </div>
            <CardTitle className="text-3xl font-serif font-bold text-white mb-2">
              Sistema PGR
            </CardTitle>
            <CardDescription className="text-blue-100 text-sm font-medium">
              Controle de Processos Administrativos
            </CardDescription>
          </CardHeader>

          {/* Corpo do formulário */}
          <CardContent className="px-8 py-8">
            <div className="mb-6 text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-50 rounded-full mb-4">
                <Shield className="h-8 w-8 text-blue-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-800 mb-2 font-sans">
                Acesso ao Sistema
              </h2>
              <p className="text-sm text-gray-500 font-sans">
                Entre com suas credenciais para continuar
              </p>
            </div>

            <form className="space-y-5" onSubmit={handleSubmit}>
              {/* Campo de usuário */}
              <div className="space-y-2">
                <Label htmlFor="username" className="font-sans">
                  Usuário
                </Label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <User className="h-5 w-5 text-gray-400" />
                  </div>
                  <Input
                    id="username"
                    name="username"
                    type="text"
                    required
                    autoComplete="username"
                    className="pl-10 font-sans"
                    placeholder="Digite seu usuário"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    disabled={loading}
                  />
                </div>
              </div>

              {/* Campo de senha */}
              <div className="space-y-2">
                <Label htmlFor="password" className="font-sans">
                  Senha
                </Label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-gray-400" />
                  </div>
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    required
                    autoComplete="current-password"
                    className="pl-10 pr-10 font-sans"
                    placeholder="Digite sua senha"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={loading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 transition-colors focus:outline-none"
                    tabIndex={-1}
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5" />
                    ) : (
                      <Eye className="h-5 w-5" />
                    )}
                  </button>
                </div>
              </div>

              {/* Botão de submit */}
              <div className="pt-2">
                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-[#1A2B3C] hover:bg-[#2D3436] text-white font-semibold"
                  size="lg"
                >
                  {loading ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span className="font-sans">Entrando...</span>
                    </>
                  ) : (
                    <>
                      <LogIn className="h-5 w-5" />
                      <span className="font-sans">Entrar no Sistema</span>
                    </>
                  )}
                </Button>
              </div>
            </form>
          </CardContent>

          {/* Footer do card */}
          <CardFooter className="pt-6 border-t border-gray-200">
            <p className="text-xs text-center text-gray-500 w-full font-sans">
              © 2024 Sistema PGR - Procuradoria Geral da República
            </p>
          </CardFooter>
        </Card>

        {/* Informações de segurança */}
        <div className="mt-6 text-center">
          <p className="text-sm text-white/80 flex items-center justify-center gap-2 font-sans">
            <Shield className="h-4 w-4" />
            <span>Acesso seguro e criptografado</span>
          </p>
        </div>
      </div>

      <style>{`
        @keyframes blob {
          0%, 100% {
            transform: translate(0, 0) scale(1);
          }
          33% {
            transform: translate(30px, -50px) scale(1.1);
          }
          66% {
            transform: translate(-20px, 20px) scale(0.9);
          }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  )
}
