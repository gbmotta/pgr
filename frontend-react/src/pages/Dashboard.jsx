import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { 
  FileText, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  Search,
  Eye
} from 'lucide-react'
import { useState } from 'react'
import toast from 'react-hot-toast'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function Dashboard() {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const { data: statistics, isLoading: statsLoading } = useQuery({
    queryKey: ['statistics'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/statistics/summary`)
      return response.data
    },
  })

  const { data: processes, isLoading: processesLoading } = useQuery({
    queryKey: ['processes'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/processes`)
      const processes = response.data
      // Buscar detalhes completos
      const details = await Promise.all(
        processes.map(async (proc) => {
          try {
            const detailResponse = await axios.get(`${API_URL}/processes/${proc.protocol_number}`)
            return detailResponse.data
          } catch {
            return proc
          }
        })
      )
      return details
    },
  })

  const { data: overdueDeadlines } = useQuery({
    queryKey: ['overdue-deadlines'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/deadlines/overdue`)
      return response.data
    },
  })

  const filteredProcesses = processes?.filter(
    (proc) =>
      proc.protocol_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      proc.applicant_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      proc.applicant_registration?.includes(searchTerm)
  )

  if (statsLoading || processesLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const statusColors = {
    RECEBIDO: 'bg-blue-100 text-blue-800',
    EM_ANALISE: 'bg-yellow-100 text-yellow-800',
    PENDENTE_DOCS: 'bg-orange-100 text-orange-800',
    DEFERIDO: 'bg-green-100 text-green-800',
    INDEFERIDO: 'bg-red-100 text-red-800',
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">Visão geral dos processos administrativos</p>
      </div>

      {/* Cards de resumo */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <FileText className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total de Processos</dt>
                  <dd className="text-lg font-medium text-gray-900">{statistics?.total_processes || 0}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Clock className="h-6 w-6 text-yellow-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Em Análise</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {statistics?.by_status?.EM_ANALISE || 0}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <AlertCircle className="h-6 w-6 text-orange-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Pendente Docs</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {statistics?.by_status?.PENDENTE_DOCS || 0}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <AlertCircle className="h-6 w-6 text-red-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Prazos Vencidos</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {statistics?.overdue_deadlines || 0}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Busca */}
      <div className="mb-6">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
            placeholder="Buscar por protocolo, nome ou matrícula..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {/* Lista de processos */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {filteredProcesses?.map((process) => (
            <li key={process.protocol_number}>
              <div
                className="px-4 py-4 sm:px-6 hover:bg-gray-50 cursor-pointer"
                onClick={() => navigate(`/process/${process.protocol_number}`)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <FileText className="h-5 w-5 text-gray-400" />
                    </div>
                    <div className="ml-4">
                      <div className="text-sm font-medium text-primary-600">
                        {process.protocol_number}
                      </div>
                      <div className="text-sm text-gray-500">{process.applicant_name}</div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        statusColors[process.status?.code || process.status_code] || 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {process.status?.label || process.status_code}
                    </span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        navigate(`/process/${process.protocol_number}`)
                      }}
                      className="text-primary-600 hover:text-primary-800"
                    >
                      <Eye className="h-5 w-5" />
                    </button>
                  </div>
                </div>
                <div className="mt-2 sm:flex sm:justify-between">
                  <div className="sm:flex">
                    <p className="flex items-center text-sm text-gray-500">
                      Tipo: {process.type?.name || process.type_name}
                    </p>
                    {process.applicant_registration && (
                      <p className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0 sm:ml-6">
                        Matrícula: {process.applicant_registration}
                      </p>
                    )}
                  </div>
                  <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                    <p>
                      Criado em:{' '}
                      {format(new Date(process.created_date), "dd 'de' MMMM 'de' yyyy", {
                        locale: ptBR,
                      })}
                    </p>
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
        {filteredProcesses?.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">Nenhum processo encontrado</p>
          </div>
        )}
      </div>
    </div>
  )
}

