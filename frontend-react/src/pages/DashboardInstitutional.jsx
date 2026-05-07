import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { useNavigate, useSearchParams, Link } from 'react-router-dom'
import { 
  Search,
  Filter,
  X,
  FolderOpen,
  Upload,
  AlertTriangle,
  CalendarDays,
  FileBarChart2,
  ArrowRight,
  Scale,
  SlidersHorizontal,
} from 'lucide-react'
import { useState, useMemo, useEffect } from 'react'
import LegalProcessTable from '../components/tables/LegalProcessTable'
import { API_URL } from '@/lib/apiConfig'
import { EmptyState } from '@/components/ui/empty-state'
import { DashboardTableSkeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'

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
  const [searchParams] = useSearchParams()
  const [searchTerm, setSearchTerm] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [filterPrazoInicio, setFilterPrazoInicio] = useState('')
  const [filterPrazoFim, setFilterPrazoFim] = useState('')
  const [filterDataRecebimento, setFilterDataRecebimento] = useState('')
  const alertWindowDays = 7 // Dias antes do prazo para alertar

  useEffect(() => {
    const q = searchParams.get('q')
    if (q != null && q !== '') {
      setSearchTerm(q)
    }
  }, [searchParams])

  const { data: processes = [], isLoading } = useQuery({
    queryKey: ['processes'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/processes`)
      return response.data || []
    },
  })

  const { data: statistics } = useQuery({
    queryKey: ['statistics-dashboard'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/statistics/summary`)
      return response.data
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

  const processHealth = useMemo(() => {
    const summary = {
      critical: 0,
      upcoming: 0,
      withoutDeadline: 0,
    }

    filteredProcesses.forEach((proc) => {
      const prazoDate = parsePrazoDate(proc.prazo_final)
      if (!prazoDate) {
        summary.withoutDeadline += 1
        return
      }
      const today = new Date()
      const normalizedToday = new Date(today.getFullYear(), today.getMonth(), today.getDate())
      const daysUntil = Math.ceil((prazoDate - normalizedToday) / (1000 * 60 * 60 * 24))
      if (daysUntil <= 7) {
        summary.critical += 1
      } else if (daysUntil <= 30) {
        summary.upcoming += 1
      }
    })

    return summary
  }, [filteredProcesses])

  const activeFilterChips = [
    searchTerm ? `Pesquisa: "${searchTerm}"` : null,
    filterPrazoInicio ? `Prazo de ${filterPrazoInicio}` : null,
    filterPrazoFim ? `Prazo até ${filterPrazoFim}` : null,
    filterDataRecebimento ? `Recebimento ${filterDataRecebimento}` : null,
  ].filter(Boolean)


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
      <div className="space-y-6">
        <div className="bg-white border border-neutral-border p-6 rounded-lg">
          <DashboardTableSkeleton />
        </div>
      </div>
    )
  }

  const emptyTableContent =
    processes.length === 0 ? (
      <EmptyState
        icon={FolderOpen}
        title="Ainda não tem processos nesta conta"
        description="Importe uma planilha (Excel, CSV ou Google Sheets), use a grelha no PGR ou carregue um ficheiro na página de importação."
      >
        <Button asChild>
          <Link to="/upload">
            <Upload className="h-4 w-4 mr-2 inline" aria-hidden />
            Ir para importar dados
          </Link>
        </Button>
      </EmptyState>
    ) : (
      <EmptyState
        icon={Search}
        title="Nenhum processo corresponde aos filtros"
        description="Ajuste a pesquisa ou limpe os filtros para voltar a ver todos os processos."
      >
        <Button type="button" variant="secondary" onClick={clearFilters}>
          Limpar pesquisa e filtros
        </Button>
      </EmptyState>
    )

  return (
    <div className="space-y-6">
      <section className="surface-panel overflow-hidden">
        <div className="grid gap-6 px-6 py-6 lg:grid-cols-[1.5fr_0.9fr] lg:px-8">
          <div>
            <span className="hero-badge">
              <Scale className="h-3.5 w-3.5" />
              Operação jurídica central
            </span>
            <h1 className="page-title mt-4">Controle de Processos Administrativos</h1>
            <p className="page-subtitle mt-3">
              Acompanhe a carteira processual com leitura rápida de prazos, filtros mais claros e acesso
              direto às ações mais frequentes da equipa.
            </p>
            <div className="mt-5 flex flex-wrap gap-3">
              <Button asChild>
                <Link to="/upload">
                  <Upload className="h-4 w-4" />
                  Importar novos dados
                </Link>
              </Button>
              <Button variant="outline" asChild>
                <Link to="/reports">
                  <FileBarChart2 className="h-4 w-4" />
                  Abrir relatórios
                </Link>
              </Button>
              <Button variant="secondary" asChild>
                <Link to="/calendar">
                  <CalendarDays className="h-4 w-4" />
                  Ver calendário
                </Link>
              </Button>
            </div>
          </div>
          <div className="surface-panel-muted flex flex-col justify-between p-5">
            <div>
              <p className="section-kicker">Resumo da carteira</p>
              <div className="mt-3 grid gap-3 sm:grid-cols-3 lg:grid-cols-1">
                <div className="rounded-2xl bg-white px-4 py-3">
                  <div className="metric-label">Processos visíveis</div>
                  <div className="mt-2 text-3xl font-semibold text-[#182534]">{filteredProcesses.length}</div>
                </div>
                <div className="rounded-2xl bg-white px-4 py-3">
                  <div className="metric-label">Prazos críticos</div>
                  <div className="mt-2 text-3xl font-semibold text-[#a53b2d]">{processHealth.critical}</div>
                </div>
                <div className="rounded-2xl bg-white px-4 py-3">
                  <div className="metric-label">Sem prazo final</div>
                  <div className="mt-2 text-3xl font-semibold text-[#6d7785]">{processHealth.withoutDeadline}</div>
                </div>
              </div>
            </div>
            <p className="mt-4 text-sm leading-6 text-[#5f6d7d]">
              Total geral da conta: <strong>{statistics?.total_processes ?? processes.length}</strong>. Use os
              filtros abaixo para refinar a triagem.
            </p>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <article className="metric-card">
          <div className="flex items-center justify-between">
            <span className="metric-label">Prazos críticos</span>
            <AlertTriangle className="h-5 w-5 text-[#a53b2d]" />
          </div>
          <div className="metric-value">{processHealth.critical}</div>
          <p className="metric-note">Processos com prazo final já vencido ou dentro dos próximos 7 dias.</p>
        </article>
        <article className="metric-card">
          <div className="flex items-center justify-between">
            <span className="metric-label">Janela de atenção</span>
            <CalendarDays className="h-5 w-5 text-[#9a6b14]" />
          </div>
          <div className="metric-value">{processHealth.upcoming}</div>
          <p className="metric-note">Itens que entram na zona de atenção entre 8 e 30 dias.</p>
        </article>
        <article className="metric-card">
          <div className="flex items-center justify-between">
            <span className="metric-label">Fluxo operacional</span>
            <ArrowRight className="h-5 w-5 text-[#345a7c]" />
          </div>
          <div className="metric-value">{hasActiveFilters ? filteredProcesses.length : processes.length}</div>
          <p className="metric-note">
            {hasActiveFilters ? 'Resultados após aplicar os filtros atuais.' : 'Base completa pronta para triagem.'}
          </p>
        </article>
      </section>

      <section className="surface-panel p-6">
        <div className="space-y-4">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="section-kicker">Pesquisa e refinamento</p>
              <h2 className="mt-1 text-xl font-semibold text-[#182534]">Encontre processos sem perder contexto</h2>
            </div>
            <Button type="button" variant="outline" onClick={() => setShowFilters(!showFilters)}>
              <SlidersHorizontal className="h-4 w-4" />
              {showFilters ? 'Recolher filtros' : 'Abrir filtros avançados'}
            </Button>
          </div>

          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-neutral-text-tertiary" aria-hidden />
            </div>
            <input
              type="search"
              className="institutional-input !pl-12 !pr-10 !rounded-2xl !border-[#d4dbe3] !bg-[#fcfcfb] !py-3 !shadow-[0_10px_20px_-24px_rgba(15,23,42,0.6)]"
              placeholder="Buscar por PROCESSO ADM 1DOC, PROCESSO JUDICIAL, PARTES, TEMA, PRAZO, TIPO DE ATO..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              aria-label="Pesquisar processos"
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
            <div className="flex items-center gap-2 text-sm text-[#637081]">
              <Filter className="h-5 w-5" />
              <span>{hasActiveFilters ? 'Filtros ativos aplicados' : 'Nenhum filtro além da pesquisa textual'}</span>
            </div>
            
            {hasActiveFilters && (
              <button
                onClick={clearFilters}
                className="text-xs font-medium text-status-indeferido hover:text-status-vencido"
              >
                Limpar filtros
              </button>
            )}
          </div>

          {activeFilterChips.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {activeFilterChips.map((chip) => (
                <span key={chip} className="filter-chip">
                  {chip}
                </span>
              ))}
            </div>
          )}

          {showFilters && (
            <div className="grid grid-cols-1 gap-4 border-t border-neutral-border pt-4 md:grid-cols-3">
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
      </section>

      <section className="space-y-3">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="section-kicker">Lista operacional</p>
            <h2 className="text-xl font-semibold text-[#182534]">Processos filtrados</h2>
          </div>
          <p className="text-sm text-[#627182]">
            {filteredProcesses.length} resultado(s) {hasActiveFilters ? 'com filtros ativos' : 'na base atual'}.
          </p>
        </div>

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
          emptyContent={emptyTableContent}
        />
      </section>
    </div>
  )
}
