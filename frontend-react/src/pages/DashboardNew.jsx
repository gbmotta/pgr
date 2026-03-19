import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { 
  FileText, 
  Search,
  ChevronDown,
  ChevronUp,
  Calendar,
  Gavel,
  Filter,
  X,
  Clock
} from 'lucide-react'
import { useState, useMemo } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'

// Função para obter cor baseada na string da cor (visual jurídico profissional)
const getColorClasses = (color) => {
  const colors = {
    green: 'bg-emerald-50 text-emerald-800 border-emerald-300 font-semibold shadow-sm',
    yellow: 'bg-amber-50 text-amber-800 border-amber-300 font-semibold shadow-sm',
    orange: 'bg-orange-50 text-orange-800 border-orange-300 font-semibold shadow-sm',
    red: 'bg-red-50 text-red-800 border-red-300 font-semibold shadow-sm',
  }
  return colors[color] || 'bg-gray-50 text-gray-700 border-gray-200'
}

// Função para parse de data no formato DD/MM para comparação
const parsePrazoDate = (prazoStr) => {
  if (!prazoStr) return null
  const [day, month] = prazoStr.split('/').map(Number)
  if (!day || !month) return null
  const now = new Date()
  const year = now.getFullYear()
  const prazoDate = new Date(year, month - 1, day)
  // Se já passou este ano, considerar próximo ano
  if (prazoDate < now) {
    prazoDate.setFullYear(year + 1)
  }
  return prazoDate
}

// Função para parse de mês/ano
const parseMesAno = (mesAnoStr) => {
  if (!mesAnoStr) return null
  const meses = {
    'JAN': 0, 'FEV': 1, 'MAR': 2, 'ABR': 3, 'MAI': 4, 'JUN': 5,
    'JUL': 6, 'AGO': 7, 'SET': 8, 'OUT': 9, 'NOV': 10, 'DEZ': 11
  }
  const partes = mesAnoStr.toUpperCase().split('/')
  if (partes.length !== 2) return null
  const mes = meses[partes[0]]
  const ano = parseInt(partes[1])
  if (mes === undefined || isNaN(ano)) return null
  return new Date(ano, mes, 1)
}

export default function DashboardNew() {
  const [searchTerm, setSearchTerm] = useState('')
  const [expandedProcess, setExpandedProcess] = useState(null)
  const [showFilters, setShowFilters] = useState(false)
  const [filterPrazoInicio, setFilterPrazoInicio] = useState('')
  const [filterPrazoFim, setFilterPrazoFim] = useState('')
  const [filterDataRecebimento, setFilterDataRecebimento] = useState('')

  const { data: processes = [], isLoading } = useQuery({
    queryKey: ['processes'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/processes`)
      return response.data || []
    },
  })

  // Função de busca e filtros avançados
  const filteredProcesses = useMemo(() => {
    if (!processes.length) return []

    return processes.filter((proc) => {
      // Busca por texto (IDs, partes, tema-observações)
      if (searchTerm) {
        const search = searchTerm.toLowerCase()
        const matchesSearch = 
          (proc.processo_adm_1doc && proc.processo_adm_1doc.toLowerCase().includes(search)) ||
          (proc.processo_judicial && proc.processo_judicial.toLowerCase().includes(search)) ||
          (proc.partes && proc.partes.toLowerCase().includes(search)) ||
          (proc.tema_observacoes && proc.tema_observacoes.toLowerCase().includes(search)) ||
          (proc.data_recebimento_mes_ano && proc.data_recebimento_mes_ano.toLowerCase().includes(search)) ||
          (proc.tipo_ato && proc.tipo_ato.toLowerCase().includes(search))
        
        if (!matchesSearch) return false
      }

      // Filtro por prazo (range)
      if (filterPrazoInicio || filterPrazoFim) {
        const prazoDate = parsePrazoDate(proc.prazo_final)
        if (!prazoDate) return false

        if (filterPrazoInicio) {
          const inicioDate = parsePrazoDate(filterPrazoInicio)
          if (inicioDate && prazoDate < inicioDate) return false
        }

        if (filterPrazoFim) {
          const fimDate = parsePrazoDate(filterPrazoFim)
          if (fimDate && prazoDate > fimDate) return false
        }
      }

      // Filtro por data de recebimento
      if (filterDataRecebimento) {
        const procDate = parseMesAno(proc.data_recebimento_mes_ano)
        const filterDate = parseMesAno(filterDataRecebimento)
        if (!procDate || !filterDate) return false
        if (procDate.getMonth() !== filterDate.getMonth() || 
            procDate.getFullYear() !== filterDate.getFullYear()) {
          return false
        }
      }

      return true
    })
  }, [processes, searchTerm, filterPrazoInicio, filterPrazoFim, filterDataRecebimento])

  const toggleExpand = (processId) => {
    setExpandedProcess(expandedProcess === processId ? null : processId)
  }

  const clearFilters = () => {
    setSearchTerm('')
    setFilterPrazoInicio('')
    setFilterPrazoFim('')
    setFilterDataRecebimento('')
  }

  const hasActiveFilters = searchTerm || filterPrazoInicio || filterPrazoFim || filterDataRecebimento

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-800"></div>
      </div>
    )
  }

  return (
    <div className="h-full bg-gradient-to-br from-slate-50 to-blue-50 overflow-auto">
      <div className="px-4 sm:px-6 lg:px-8 py-6">
        {/* Cabeçalho com visual jurídico */}
        <div className="mb-8 bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="bg-blue-100 p-3 rounded-lg">
                <Gavel className="h-8 w-8 text-blue-800" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900 font-serif">
                  Controle de Processos
                </h1>
                <p className="mt-1 text-gray-600 font-medium">
                  Sistema de Gestão de Processos Administrativos e Judiciais
                </p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-500">Total de processos</div>
              <div className="text-2xl font-bold text-blue-800">{filteredProcesses.length}</div>
            </div>
          </div>
        </div>

        {/* Barra de busca e filtros */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6 border border-gray-200">
          <div className="space-y-4">
            {/* Busca principal */}
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                className="block w-full pl-12 pr-4 py-3 border-2 border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base font-medium"
                placeholder="Buscar por número do processo, partes, tema, observações, tipo de ato..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              {searchTerm && (
                <button
                  onClick={() => setSearchTerm('')}
                  className="absolute inset-y-0 right-0 pr-4 flex items-center"
                >
                  <X className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                </button>
              )}
            </div>

            {/* Botão de filtros avançados */}
            <div className="flex items-center justify-between">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center space-x-2 text-blue-700 hover:text-blue-800 font-medium"
              >
                <Filter className="h-5 w-5" />
                <span>Filtros Avançados</span>
                {showFilters && <ChevronUp className="h-4 w-4" />}
                {!showFilters && <ChevronDown className="h-4 w-4" />}
              </button>
              
              {hasActiveFilters && (
                <button
                  onClick={clearFilters}
                  className="text-sm text-red-600 hover:text-red-800 font-medium"
                >
                  Limpar filtros
                </button>
              )}
            </div>

            {/* Filtros avançados (expansível) */}
            {showFilters && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-gray-200">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Prazo Final (De): DD/MM
                  </label>
                  <input
                    type="text"
                    placeholder="Ex: 01/02"
                    value={filterPrazoInicio}
                    onChange={(e) => setFilterPrazoInicio(e.target.value)}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Prazo Final (Até): DD/MM
                  </label>
                  <input
                    type="text"
                    placeholder="Ex: 31/12"
                    value={filterPrazoFim}
                    onChange={(e) => setFilterPrazoFim(e.target.value)}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Data Recebimento: MÊS/ANO
                  </label>
                  <input
                    type="text"
                    placeholder="Ex: DEZ/2025"
                    value={filterDataRecebimento}
                    onChange={(e) => setFilterDataRecebimento(e.target.value.toUpperCase())}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Lista de processos com visual jurídico */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden border border-gray-200">
          <div className="bg-gradient-to-r from-blue-800 to-blue-900 px-6 py-4">
            <h2 className="text-lg font-bold text-white font-serif">
              Processos Registrados
            </h2>
          </div>
          
          {filteredProcesses.length === 0 ? (
            <div className="text-center py-16">
              <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p className="text-gray-500 text-lg font-medium">
                {hasActiveFilters 
                  ? 'Nenhum processo encontrado com os filtros aplicados'
                  : 'Nenhum processo cadastrado'}
              </p>
            </div>
          ) : (
            <ul className="divide-y divide-gray-200">
              {filteredProcesses.map((process) => (
                <li key={process.id} className="hover:bg-blue-50 transition-colors">
                  <div className="px-6 py-5">
                    {/* Cabeçalho do processo */}
                    <div className="flex items-start justify-between mb-4">
                      {/* Primeira caixa: IDs dos processos */}
                      <div className="flex-1">
                        <div className="flex items-center space-x-4 mb-3">
                          {process.processo_adm_1doc && (
                            <div className="inline-flex items-center space-x-2 bg-blue-100 px-4 py-2 rounded-lg border border-blue-300">
                              <FileText className="h-4 w-4 text-blue-700" />
                              <div>
                                <div className="text-xs font-medium text-blue-600 uppercase tracking-wide">Processo ADM 1DOC</div>
                                <div className="text-sm font-bold text-blue-900">{process.processo_adm_1doc}</div>
                              </div>
                            </div>
                          )}
                          {process.processo_judicial && (
                            <div className="inline-flex items-center space-x-2 bg-purple-100 px-4 py-2 rounded-lg border border-purple-300">
                              <Gavel className="h-4 w-4 text-purple-700" />
                              <div>
                                <div className="text-xs font-medium text-purple-600 uppercase tracking-wide">Processo Judicial</div>
                                <div className="text-sm font-bold text-purple-900">{process.processo_judicial}</div>
                              </div>
                            </div>
                          )}
                          {!process.processo_adm_1doc && !process.processo_judicial && (
                            <div className="text-sm text-gray-500 italic">Processo sem identificação</div>
                          )}
                        </div>
                      </div>

                      {/* Segunda caixa: Prazos com cores destacadas */}
                      <div className="flex items-center space-x-3 ml-4">
                        {process.prazo_info_estag && (
                          <div className="flex items-center space-x-2 text-gray-700">
                            <Clock className="h-4 w-4 text-gray-500" />
                            <span className="text-sm font-medium">Info: {process.prazo_info_estag}</span>
                          </div>
                        )}
                        {process.prazo_final && (
                          <div className={`px-4 py-2 rounded-lg border-2 text-sm font-bold ${getColorClasses(process.prazo_color)}`}>
                            Prazo Final: {process.prazo_final}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Terceira caixa: Data de recebimento */}
                    {process.data_recebimento_mes_ano && (
                      <div className="mb-3 flex items-center space-x-2 text-gray-600">
                        <Calendar className="h-4 w-4 text-gray-400" />
                        <span className="text-sm font-medium">
                          Data de Recebimento: <span className="font-semibold text-gray-800">{process.data_recebimento_mes_ano}</span>
                        </span>
                      </div>
                    )}

                    {/* Quarta caixa: Expandível com PARTES e TEMA-OBSERVAÇÕES */}
                    {(process.partes || process.tema_observacoes) && (
                      <div className="mt-4">
                        <button
                          onClick={() => toggleExpand(process.id)}
                          className="flex items-center space-x-2 text-blue-700 hover:text-blue-800 font-semibold transition-colors"
                        >
                          {expandedProcess === process.id ? (
                            <>
                              <ChevronUp className="h-5 w-5" />
                              <span>Ocultar Detalhes</span>
                            </>
                          ) : (
                            <>
                              <ChevronDown className="h-5 w-5" />
                              <span>Ver Detalhes Completos</span>
                            </>
                          )}
                        </button>
                        
                        {expandedProcess === process.id && (
                          <div className="mt-3 p-4 bg-slate-50 rounded-lg border border-gray-200 space-y-4">
                            {process.partes && (
                              <div>
                                <div className="text-xs font-bold text-gray-700 uppercase tracking-wide mb-2 flex items-center space-x-2">
                                  <FileText className="h-3 w-3" />
                                  <span>Partes Envolvidas</span>
                                </div>
                                <div className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed bg-white p-3 rounded border border-gray-200">
                                  {process.partes}
                                </div>
                              </div>
                            )}
                            {process.tema_observacoes && (
                              <div>
                                <div className="text-xs font-bold text-gray-700 uppercase tracking-wide mb-2 flex items-center space-x-2">
                                  <FileText className="h-3 w-3" />
                                  <span>Tema e Observações</span>
                                </div>
                                <div className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed bg-white p-3 rounded border border-gray-200">
                                  {process.tema_observacoes}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Informações de controle interno (discretas) */}
                    {(process.tipo_ato || process.data_realizacao_ato) && (
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <div className="flex items-center space-x-4 text-xs text-gray-400">
                          {process.tipo_ato && (
                            <span className="flex items-center space-x-1">
                              <FileText className="h-3 w-3" />
                              <span>Tipo: {process.tipo_ato}</span>
                            </span>
                          )}
                          {process.data_realizacao_ato && (
                            <span className="flex items-center space-x-1">
                              <Calendar className="h-3 w-3" />
                              <span>Realizado em: {process.data_realizacao_ato}</span>
                            </span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}
