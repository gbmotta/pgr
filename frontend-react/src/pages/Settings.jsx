import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import axios from 'axios'
import toast from 'react-hot-toast'
import {
  User,
  Lock,
  Shield,
  Cloud,
  Table2,
  FileUp,
  Link2,
  Copy,
  Loader2,
} from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { API_URL } from '@/lib/apiConfig'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

const IMPORT_MODE_KEY = 'pgr_import_mode_preference'
const IMPORT_MODES = [
  {
    id: 'grid',
    label: 'Planilha no PGR',
    description: 'Grelha no browser — sem ficheiro nem Google.',
    icon: Table2,
  },
  {
    id: 'file',
    label: 'Só ficheiro',
    description: 'Upload Excel/CSV local (sem sincronização Google).',
    icon: FileUp,
  },
  {
    id: 'google_drive',
    label: 'Google Sheets + partilha',
    description: 'Planilha no seu Drive; partilha com a service account como leitor.',
    icon: Link2,
  },
]

export default function Settings() {
  const { user, refreshUser } = useAuth()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [importMode, setImportMode] = useState(() => {
    if (typeof window === 'undefined') return 'grid'
    return localStorage.getItem(IMPORT_MODE_KEY) || 'grid'
  })

  useEffect(() => {
    if (user) {
      setFullName(user.full_name || '')
      setEmail(user.email || '')
    }
  }, [user])

  const { data: saInfo, isLoading: saLoading } = useQuery({
    queryKey: ['settings-service-account'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/sheets/service-account-email`)
      return res.data
    },
    retry: false,
  })

  const { data: linkedSheets = [] } = useQuery({
    queryKey: ['linked-sheets'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/sheets/linked`)
      return res.data
    },
  })

  const profileMutation = useMutation({
    mutationFn: async () => {
      const body = {}
      const prevName = (user?.full_name || '').trim()
      const prevEmail = (user?.email || '').trim()
      if (fullName.trim() !== prevName) {
        body.full_name = fullName.trim() || null
      }
      if (email.trim() !== prevEmail) {
        body.email = email.trim()
      }
      if (Object.keys(body).length === 0) {
        return Promise.reject(new Error('__no_changes'))
      }
      const res = await axios.patch(`${API_URL}/api/auth/profile`, body)
      return res.data
    },
    onSuccess: async () => {
      toast.success('Perfil atualizado.')
      await refreshUser()
    },
    onError: (e) => {
      if (e.message === '__no_changes') {
        toast.info('Nenhuma alteração no perfil.')
        return
      }
      toast.error(e.response?.data?.detail || 'Erro ao guardar perfil')
    },
  })

  const passwordMutation = useMutation({
    mutationFn: async () => {
      const res = await axios.post(`${API_URL}/api/auth/change-password`, {
        current_password: currentPassword,
        new_password: newPassword,
      })
      return res.data
    },
    onSuccess: () => {
      toast.success('Palavra-passe alterada.')
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
    },
    onError: (e) => {
      toast.error(e.response?.data?.detail || 'Erro ao alterar palavra-passe')
    },
  })

  const handleSaveProfile = (e) => {
    e.preventDefault()
    if (!email.trim()) {
      toast.error('O email é obrigatório.')
      return
    }
    profileMutation.mutate()
  }

  const handleChangePassword = (e) => {
    e.preventDefault()
    if (newPassword.length < 8) {
      toast.error('A nova palavra-passe deve ter pelo menos 8 caracteres.')
      return
    }
    if (newPassword !== confirmPassword) {
      toast.error('A confirmação não coincide com a nova palavra-passe.')
      return
    }
    passwordMutation.mutate()
  }

  const persistImportMode = (id) => {
    setImportMode(id)
    localStorage.setItem(IMPORT_MODE_KEY, id)
    toast.success('Preferência guardada neste dispositivo.')
  }

  const copySaEmail = () => {
    const em = saInfo?.service_account_email
    if (!em) return
    navigator.clipboard.writeText(em)
    toast.success('Email copiado.')
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Configurações</h1>
        <p className="text-sm text-gray-600 mt-1">
          Perfil, segurança, privacidade e integração com Google Sheets.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <User className="h-5 w-5 text-gray-500" />
            Perfil
          </CardTitle>
          <CardDescription>Nome e email da sua conta PGR.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSaveProfile} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Utilizador</label>
              <input
                type="text"
                value={user?.username || ''}
                disabled
                className="w-full rounded-md border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-600"
              />
              <p className="text-xs text-gray-500 mt-1">O nome de utilizador não pode ser alterado.</p>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Nome completo</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                placeholder="O seu nome"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
              />
            </div>
            {user?.is_admin && (
              <p className="text-xs text-amber-800 bg-amber-50 border border-amber-200 rounded-md px-3 py-2">
                Esta conta tem perfil de <strong>administrador</strong>.
              </p>
            )}
            <Button type="submit" disabled={profileMutation.isPending}>
              {profileMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  A guardar…
                </>
              ) : (
                'Guardar perfil'
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Lock className="h-5 w-5 text-gray-500" />
            Palavra-passe
          </CardTitle>
          <CardDescription>Altere a palavra-passe de acesso ao PGR.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleChangePassword} className="space-y-4 max-w-md">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Palavra-passe atual</label>
              <input
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                autoComplete="current-password"
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Nova palavra-passe</label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                autoComplete="new-password"
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                required
                minLength={8}
              />
              <p className="text-xs text-gray-500 mt-1">Mínimo de 8 caracteres.</p>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Confirmar nova palavra-passe</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                autoComplete="new-password"
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                required
              />
            </div>
            <Button type="submit" variant="secondary" disabled={passwordMutation.isPending}>
              {passwordMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  A atualizar…
                </>
              ) : (
                'Alterar palavra-passe'
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Shield className="h-5 w-5 text-gray-500" />
            Privacidade e os seus dados
          </CardTitle>
          <CardDescription>Como o PGR trata a informação por advogado / conta.</CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-gray-700 space-y-3">
          <p>
            <strong>Isolamento:</strong> cada conta vê apenas os processos e planilhas associados ao seu
            utilizador. Não há partilha de listagens entre contas no mesmo servidor.
          </p>
          <p>
            <strong>Onde ficam os dados:</strong> os processos importados ou criados na grelha são guardados na
            base de dados do PGR (servidor da aplicação). Ficheiros que enviar no upload são tratados no
            servidor para importação.
          </p>
          <p>
            <strong>Google Drive:</strong> as folhas de cálculo continuam na sua conta Google. A{' '}
            <em>service account</em> só lê o que partilhar explicitamente como <strong>Leitor</strong>.
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Cloud className="h-5 w-5 text-gray-500" />
            Modo de trabalho preferido
          </CardTitle>
          <CardDescription>
            Preferência guardada neste navegador (ao abrir{' '}
            <Link to="/upload" className="text-blue-600 hover:underline">
              Upload
            </Link>{' '}
            pode usar o separador correspondente).
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid gap-2">
            {IMPORT_MODES.map(({ id, label, description, icon: Icon }) => (
              <label
                key={id}
                className={`flex cursor-pointer items-start gap-3 rounded-lg border p-3 transition-colors ${
                  importMode === id
                    ? 'border-blue-500 bg-blue-50/50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <input
                  type="radio"
                  name="importMode"
                  checked={importMode === id}
                  onChange={() => persistImportMode(id)}
                  className="mt-1"
                />
                <Icon className="h-5 w-5 text-gray-500 shrink-0 mt-0.5" />
                <div>
                  <div className="font-medium text-gray-900 text-sm">{label}</div>
                  <div className="text-xs text-gray-600">{description}</div>
                </div>
              </label>
            ))}
          </div>
          <Button variant="outline" asChild>
            <Link to="/upload">Ir para importação / planilha</Link>
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Link2 className="h-5 w-5 text-gray-500" />
            Google Sheets (service account)
          </CardTitle>
          <CardDescription>
            Email para partilhar planilhas como leitor. Monitorizadas agora:{' '}
            <strong>{linkedSheets.length}</strong>.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {saLoading && (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Loader2 className="h-4 w-4 animate-spin" /> A carregar…
            </div>
          )}
          {!saLoading && saInfo?.service_account_email && (
            <div className="flex flex-wrap items-center gap-2">
              <code className="flex-1 min-w-[12rem] rounded-md border bg-slate-50 px-3 py-2 text-sm break-all">
                {saInfo.service_account_email}
              </code>
              <Button type="button" variant="outline" size="sm" onClick={copySaEmail}>
                <Copy className="h-4 w-4 mr-1" />
                Copiar
              </Button>
            </div>
          )}
          {!saLoading && !saInfo?.service_account_email && (
            <p className="text-sm text-amber-800 bg-amber-50 border border-amber-200 rounded-md p-3">
              Não foi possível obter o email da service account (credenciais Google não configuradas no
              servidor).
            </p>
          )}
          {saInfo?.privacy_note && (
            <p className="text-xs text-gray-600 border-l-2 border-gray-300 pl-3">{saInfo.privacy_note}</p>
          )}
          {saInfo?.instructions && (
            <pre className="text-xs text-gray-700 whitespace-pre-wrap bg-slate-50 rounded-md p-3 border border-slate-200 overflow-x-auto">
              {saInfo.instructions}
            </pre>
          )}
          <Button variant="outline" asChild>
            <Link to="/linked-sheets">Planilhas monitoradas</Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
