import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { 
  Search,
  Filter,
  X
} from 'lucide-react'
import { useState, useMemo } from 'react'
import LegalProcessTable from '../components/tables/LegalProcessTable'
import { API_URL } from '@/lib/apiConfig'

const parsePrazoDate = (prazoStr) => {
  if (!prazoStr) return null
  const [day, month] = prazoStr.split('/').map(Number)
  if (!day || !month) return null
  const now = new Date()
  const year = now.getFullYear()
  const prazoDate = new Date(year, month - 1, day)
  if (prazoDate < now) {
    prazoDate.setFullYear(year + 1)
  }
  return prazoDate
}

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


export default function DashboardInstitutional() {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [filterPrazoInicio, setFilterPrazoInicio] = useState('')
  const [filterPrazoFim, setFilterPrazoFim] = useState('')
  const [filterDataRecebimento, setFilterDataRecebimento] = useState('')
  const alertWindowDays = 7 // Dias antes do prazo para alertar

  const { data: processes = [], isLoading } = useQuery({
    queryKey: ['processes'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/processes`)
      return response.data || []
    },
  })

  const filteredProcesses = useMemo(() => {
    if (!processes.length) return []

    return processes.filter((proc) => {
      if (searchTerm) {
        const search = searchTerm.toLowerCase()
        const matchesSearch = 
          (proc.processo_adm_1doc && proc.processo_adm_1doc.toLowerCase().includes(search)) ||
          (proc.processo_judicial && proc.processo_judicial.toLowerCase().includes(search)) ||
          (proc.partes && proc.partes.toLowerCase().includes(search)) ||
          (proc.tema_observacoes && proc.tema_observacoes.toLowerCase().includes(search)) ||
          (proc.data_recebimento_mes_ano && proc.data_recebimento_mes_ano.toLowerCase().includes(search)) ||
          (proc.prazo_info_estag && proc.prazo_info_estag.toLowerCase().includes(search)) ||
          (proc.prazo_final && proc.prazo_final.toLowerCase().includes(search)) ||
          (proc.tipo_ato && proc.tipo_ato.toLowerCase().includes(search)) ||
          (proc.data_realizacao_ato && proc.data_realizacao_ato.toLowerCase().includes(search))
        
        if (!matchesSearch) return false
      }

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

  const clearFilters = () => {
    setSearchTerm('')
    setFilterPrazoInicio('')
    setFilterPrazoFim('')
    setFilterDataRecebimento('')
  }

  const hasActiveFilters = searchTerm || filterPrazoInicio || filterPrazoFim || filterDataRecebimento


  const expandableContent = (row) => (
    <div className="space-y-4 py-2">
      {row.partes && (
        <div>
          <div className="label mb-2">Partes Envolvidas</div>
          <div className="text-xs text-neutral-text-primary bg-white p-3 rounded border border-neutral-border-light whitespace-pre-wrap">
            {row.partes}
          </div>
        </div>
      )}
      {row.tema_observacoes && (
        <div>
          <div className="label mb-2">Tema e Observações</div>
          <div className="text-xs text-neutral-text-primary bg-white p-3 rounded border border-neutral-border-light whitespace-pre-wrap">
            {row.tema_observacoes}
          </div>
        </div>
      )}
    </div>
  )

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-institutional-dark"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Cabeçalho */}
      <div className="bg-white border border-neutral-border p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-neutral-text-primary mb-1">
              Controle de Processos Administrativos
            </h1>
            <p className="text-xs text-neutral-text-secondary">
              Sistema de Gestão de Processos Administrativos e Judiciais
            </p>
          </div>
          <div className="text-right">
            <div className="text-xs text-neutral-text-secondary uppercase tracking-wide mb-1">
              Total de processos
            </div>
            <div className="text-2xl font-bold text-institutional-dark">{filteredProcesses.length}</div>
          </div>
        </div>
      </div>

      {/* Barra de busca e filtros */}
      <div className="bg-white border border-neutral-border p-6">
        <div className="space-y-4">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-neutral-text-tertiary" />
            </div>
            <input
              type="text"
              className="institutional-input pl-12 pr-10"
              placeholder="Buscar por PROCESSO ADM 1DOC, PROCESSO JUDICIAL, PARTES, TEMA, PRAZO, TIPO DE ATO..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="absolute inset-y-0 right-0 pr-4 flex items-center"
              >
                <X className="h-5 w-5 text-neutral-text-tertiary hover:text-neutral-text-secondary" />
              </button>
            )}
          </div>

          <div className="flex items-center justify-between">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center space-x-2 text-institutional-primary hover:text-institutional-dark font-medium"
            >
              <Filter className="h-5 w-5" />
              <span>Filtros Avançados</span>
              {showFilters ? '↑' : '↓'}
            </button>
            
            {hasActiveFilters && (
              <button
                onClick={clearFilters}
                className="text-xs text-status-indeferido hover:text-status-vencido font-medium"
              >
                Limpar filtros
              </button>
            )}
          </div>

          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-neutral-border">
              <div>
                <label className="label">Prazo Final (De): DD/MM</label>
                <input
                  type="text"
                  placeholder="Ex: 01/02"
                  value={filterPrazoInicio}
                  onChange={(e) => setFilterPrazoInicio(e.target.value)}
                  className="institutional-input"
                />
              </div>
              <div>
                <label className="label">Prazo Final (Até): DD/MM</label>
                <input
                  type="text"
                  placeholder="Ex: 31/12"
                  value={filterPrazoFim}
                  onChange={(e) => setFilterPrazoFim(e.target.value)}
                  className="institutional-input"
                />
              </div>
              <div>
                <label className="label">Data Recebimento: MÊS/ANO</label>
                <input
                  type="text"
                  placeholder="Ex: DEZ/2025"
                  value={filterDataRecebimento}
                  onChange={(e) => setFilterDataRecebimento(e.target.value.toUpperCase())}
                  className="institutional-input"
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Tabela de Processos - Densa Jurídica */}
      <div className="w-full">
        <LegalProcessTable
          data={filteredProcesses}
          onRowClick={(row) => {
            const protocol = row.processo_adm_1doc || row.processo_judicial || row.protocol_number
            if (protocol) {
              navigate(`/process/${protocol}`)
            }
          }}
          expandableContent={expandableContent}
          keyField="id"
          alertWindowDays={alertWindowDays}
        />
      </div>
    </div>
  )
}
