import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { 
  FileText, 
  Search,
  ChevronDown,
  ChevronUp
} from 'lucide-react'
import { useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Função para obter cor baseada na string da cor
const getColorClasses = (color) => {
  const colors = {
    green: 'bg-green-100 text-green-800 border-green-300',
    yellow: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    orange: 'bg-orange-100 text-orange-800 border-orange-300',
    red: 'bg-red-100 text-red-800 border-red-300',
  }
  return colors[color] || 'bg-gray-100 text-gray-800 border-gray-300'
}

export default function DashboardNew() {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [expandedProcess, setExpandedProcess] = useState(null)

  const { data: processes = [], isLoading } = useQuery({
    queryKey: ['processes'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/processes`)
      return response.data || []
    },
  })

  const filteredProcesses = processes.filter((proc) => {
    const search = searchTerm.toLowerCase()
    return (
      (proc.processo_adm_1doc && proc.processo_adm_1doc.toLowerCase().includes(search)) ||
      (proc.processo_judicial && proc.processo_judicial.toLowerCase().includes(search)) ||
      (proc.partes && proc.partes.toLowerCase().includes(search)) ||
      (proc.tema_observacoes && proc.tema_observacoes.toLowerCase().includes(search))
    )
  })

  const toggleExpand = (processId) => {
    setExpandedProcess(expandedProcess === processId ? null : processId)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Controle de Processos</h1>
        <p className="mt-2 text-gray-600">Visão geral dos processos administrativos e judiciais</p>
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
            placeholder="Buscar por processo ADM, judicial, partes ou tema..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {/* Lista de processos */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {filteredProcesses.map((process) => (
            <li key={process.id}>
              {/* Cabeçalho do processo - sempre visível */}
              <div className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                <div className="flex items-start justify-between">
                  {/* Primeira caixa: IDs dos processos */}
                  <div className="flex-1 mr-4">
                    <div className="flex items-center space-x-4 mb-2">
                      {process.processo_adm_1doc && (
                        <div className="text-sm font-medium text-primary-600">
                          ADM 1DOC: {process.processo_adm_1doc}
                        </div>
                      )}
                      {process.processo_judicial && (
                        <div className="text-sm font-medium text-blue-600">
                          JUDICIAL: {process.processo_judicial}
                        </div>
                      )}
                      {!process.processo_adm_1doc && !process.processo_judicial && (
                        <div className="text-sm text-gray-500">Sem identificação</div>
                      )}
                    </div>
                  </div>

                  {/* Segunda caixa: Prazos com cores */}
                  <div className="flex items-center space-x-3">
                    {process.prazo_info_estag && (
                      <div className="text-sm text-gray-600">
                        Info: {process.prazo_info_estag}
                      </div>
                    )}
                    {process.prazo_final && (
                      <div className={`px-3 py-1 rounded-md border text-sm font-medium ${getColorClasses(process.prazo_color)}`}>
                        Final: {process.prazo_final}
                      </div>
                    )}
                  </div>
                </div>

                {/* Terceira caixa: Data de recebimento */}
                {process.data_recebimento_mes_ano && (
                  <div className="mt-2 text-sm text-gray-500">
                    Recebimento: {process.data_recebimento_mes_ano}
                  </div>
                )}

                {/* Quarta caixa: Expandível com PARTES e TEMA-OBSERVAÇÕES */}
                {(process.partes || process.tema_observacoes) && (
                  <div className="mt-3">
                    <button
                      onClick={() => toggleExpand(process.id)}
                      className="flex items-center text-sm text-primary-600 hover:text-primary-800"
                    >
                      {expandedProcess === process.id ? (
                        <ChevronUp className="h-4 w-4 mr-1" />
                      ) : (
                        <ChevronDown className="h-4 w-4 mr-1" />
                      )}
                      Detalhes
                    </button>
                    
                    {expandedProcess === process.id && (
                      <div className="mt-2 p-3 bg-gray-50 rounded-md space-y-2">
                        {process.partes && (
                          <div>
                            <div className="text-xs font-medium text-gray-700 mb-1">PARTES:</div>
                            <div className="text-sm text-gray-600 whitespace-pre-wrap">{process.partes}</div>
                          </div>
                        )}
                        {process.tema_observacoes && (
                          <div>
                            <div className="text-xs font-medium text-gray-700 mb-1">TEMA – OBSERVAÇÕES:</div>
                            <div className="text-sm text-gray-600 whitespace-pre-wrap">{process.tema_observacoes}</div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}

                {/* Informações adicionais (controle interno) */}
                {(process.tipo_ato || process.data_realizacao_ato) && (
                  <div className="mt-2 text-xs text-gray-400">
                    {process.tipo_ato && <span>Tipo de ato: {process.tipo_ato}</span>}
                    {process.tipo_ato && process.data_realizacao_ato && <span> • </span>}
                    {process.data_realizacao_ato && <span>Realizado em: {process.data_realizacao_ato}</span>}
                  </div>
                )}
              </div>
            </li>
          ))}
        </ul>
        {filteredProcesses.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">Nenhum processo encontrado</p>
          </div>
        )}
      </div>
    </div>
  )
}

