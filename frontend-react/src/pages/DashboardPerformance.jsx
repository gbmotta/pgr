import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  LineChart, Line, Legend 
} from 'recharts'
import { 
  TrendingUp, AlertCircle, CheckCircle, Clock, ArrowUp, ArrowDown,
  Calendar, Download, FileText
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { useNavigate } from 'react-router-dom'
import { API_URL } from '@/lib/apiConfig'

/**
 * Card de KPI com indicador de mudança
 */
const KPICard = ({ title, value, change, changeLabel, icon, trend = 'up', goal }) => {
  const trendColor = trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-orange-600' : 'text-gray-600'
  const trendBg = trend === 'up' ? 'bg-green-50' : trend === 'down' ? 'bg-orange-50' : 'bg-gray-50'
  
  return (
    <Card className="border-l-4 border-[#1A2B3C]">
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <span className="text-sm font-medium uppercase tracking-wider text-gray-600 font-sans">
            {title}
          </span>
          {icon}
        </div>
        <div className="text-3xl font-bold text-[#1A2B3C] font-sans mb-2">
          {value}
        </div>
        <div className={`inline-flex items-center gap-1 px-2 py-1 rounded ${trendBg} ${trendColor} text-sm font-semibold font-sans`}>
          {trend === 'up' ? <ArrowUp size={14} /> : <ArrowDown size={14} />}
          <span>{change}</span>
        </div>
        {changeLabel && (
          <p className="text-xs text-gray-500 mt-2 font-sans">{changeLabel}</p>
        )}
        {goal && (
          <p className="text-xs text-gray-500 mt-1 font-sans">{goal}</p>
        )}
      </CardContent>
    </Card>
  )
}

/**
 * Função para calcular risco baseado no prazo
 */
const calculateRisk = (daysUntil) => {
  if (daysUntil < 0) return { level: 'Alto', color: 'bg-red-500' }
  if (daysUntil <= 1) return { level: 'Alto', color: 'bg-red-500' }
  if (daysUntil <= 3) return { level: 'Médio', color: 'bg-orange-500' }
  return { level: 'Baixo', color: 'bg-blue-500' }
}

/**
 * Função para formatar prazo relativo
 */
const formatDeadline = (daysUntil) => {
  if (daysUntil < 0) {
    return `Há ${Math.abs(daysUntil)} ${Math.abs(daysUntil) === 1 ? 'dia' : 'dias'}`
  }
  if (daysUntil === 0) return 'Hoje'
  if (daysUntil === 1) return 'Amanhã'
  return `${daysUntil} dias`
}

export default function DashboardPerformance() {
  const navigate = useNavigate()

  // Buscar estatísticas da API
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['performance-stats'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/stats`)
      return response.data
    },
  })

  // Buscar processos com prazos críticos
  const { data: criticalProcesses, isLoading: criticalLoading } = useQuery({
    queryKey: ['critical-deadlines'],
    queryFn: async () => {
      try {
        const response = await axios.get(`${API_URL}/api/deadlines/critical?alert_window_days=7`)
        // Enriquecer com dados dos processos
        const overdue = response.data.overdue || []
        const upcoming = response.data.upcoming || []
        
        // Buscar detalhes dos processos
        const enrichedOverdue = await Promise.all(
          overdue.map(async (proc) => {
            try {
              const procDetail = await axios.get(`${API_URL}/processes/${proc.protocol_number}`)
              return {
                ...proc,
                partes: procDetail.data.partes,
                applicant_name: procDetail.data.applicant_name
              }
            } catch {
              return proc
            }
          })
        )
        
        const enrichedUpcoming = await Promise.all(
          upcoming.map(async (proc) => {
            try {
              const procDetail = await axios.get(`${API_URL}/processes/${proc.protocol_number}`)
              return {
                ...proc,
                partes: procDetail.data.partes,
                applicant_name: procDetail.data.applicant_name
              }
            } catch {
              return proc
            }
          })
        )
        
        return {
          overdue: enrichedOverdue,
          upcoming: enrichedUpcoming
        }
      } catch {
        return { overdue: [], upcoming: [] }
      }
    },
  })

  // Buscar todos os processos para cálculos adicionais
  const { data: allProcesses = [] } = useQuery({
    queryKey: ['processes'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/processes`)
      return response.data || []
    },
  })

  if (statsLoading || criticalLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#1A2B3C]"></div>
      </div>
    )
  }

  // Calcular KPIs adicionais
  const totalProcessos = stats?.total_processos || 0
  const taxaConclusao = stats?.taxa_conclusao || 0
  const prazosVencidos = stats?.prazos_vencidos || 0
  const mediaDias = stats?.media_dias_conclusao || 0

  // Calcular mudanças (simulado - em produção viria do histórico)
  const taxaConclusaoChange = taxaConclusao >= 90 ? '+2.5%' : '-1.2%'
  const volumeAtivo = totalProcessos
  const volumeChange = '-1.2%'
  const eficienciaChange = '+4.3%'
  const acordosFirmados = Math.floor(totalProcessos * 0.15) // Simulado
  const acordosChange = '+18%'

  // Dados formatados para os gráficos
  const dataTemas = stats?.temas || []
  const dataProdutividade = stats?.produtividade_mensal || []

  // Combinar processos vencidos e próximos para a tabela de alertas
  const criticalList = [
    ...(criticalProcesses?.overdue || []).map(p => ({
      ...p,
      tipo: 'Vencido',
      daysUntil: p.days_overdue ? -p.days_overdue : 0
    })),
    ...(criticalProcesses?.upcoming || []).map(p => ({
      ...p,
      tipo: 'Próximo',
      daysUntil: p.days_until || 0
    }))
  ].slice(0, 5) // Limitar a 5 itens

  // Calcular volume por tema para gráfico comparativo
  const volumeCivel = dataTemas.find(t => t.name === 'Cível')?.total || 0
  const volumeTrab = dataTemas.find(t => t.name === 'Trabalhista')?.total || 0
  const totalVolume = volumeCivel + volumeTrab

  // Dados para gráfico de barras comparativo (Cível vs Trabalhista)
  const dataComparativo = dataProdutividade.length > 0 ? dataProdutividade.map(item => ({
    mes: item.mes,
    Cível: Math.floor(item.concluidos * 0.6), // Simulado
    Trab: Math.floor(item.concluidos * 0.4)  // Simulado
  })) : []

  return (
    <div className="p-8 bg-[#F9F9F9] min-h-screen font-sans">
      {/* Cabeçalho */}
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-serif text-[#1A2B3C] font-bold">Dashboard de Performance</h1>
          <p className="text-gray-600 font-sans mt-1">
            Análise estratégica de Business Intelligence e KPIs operacionais
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" className="font-sans">
            <Calendar className="h-4 w-4 mr-2" />
            Últimos 6 meses
          </Button>
          <Button className="bg-[#1A2B3C] hover:bg-[#2D3436] text-white font-sans">
            <Download className="h-4 w-4 mr-2" />
            Exportar BI
          </Button>
        </div>
      </header>

      {/* Cards de KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <KPICard
          title="Taxa de Conclusão"
          value={`${taxaConclusao.toFixed(1)}%`}
          change={taxaConclusaoChange}
          changeLabel={taxaConclusao >= 90 ? "Meta: 90% para o período" : "Abaixo da meta"}
          icon={<TrendingUp size={20} className="text-[#1A2B3C]" />}
          trend={taxaConclusao >= 90 ? 'up' : 'down'}
        />
        <KPICard
          title="Volume Ativo"
          value={volumeAtivo.toLocaleString('pt-BR')}
          change={volumeChange}
          changeLabel="Redução no passivo cível"
          icon={<FileText size={20} className="text-[#1A2B3C]" />}
          trend="down"
        />
        <KPICard
          title="Eficiência Op."
          value="+12%"
          change={eficienciaChange}
          changeLabel="Melhoria em relação ao Q1"
          icon={<CheckCircle size={20} className="text-[#1A2B3C]" />}
          trend="up"
        />
        <KPICard
          title="Acordos Firmados"
          value={acordosFirmados}
          change={acordosChange}
          changeLabel="Economia de R$ 2.4M"
          icon={<CheckCircle size={20} className="text-[#1A2B3C]" />}
          trend="up"
        />
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Gráfico de Barras - Volume por Tema */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-lg font-semibold text-[#1A2B3C] font-sans">
                  Volume por Tema
                </CardTitle>
                <p className="text-sm text-gray-600 font-sans mt-1">
                  Distribuição Cível vs. Trabalhista
                </p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-[#1A2B3C] font-sans">{totalVolume}</p>
                <p className="text-xs text-green-600 font-sans">+5% vs. período ant.</p>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              {dataComparativo.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={dataComparativo}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                    <XAxis 
                      dataKey="mes" 
                      tick={{ fill: '#6b7280', fontSize: 12 }}
                      style={{ fontFamily: 'sans-serif' }}
                    />
                    <YAxis 
                      tick={{ fill: '#6b7280', fontSize: 12 }}
                      style={{ fontFamily: 'sans-serif' }}
                    />
                    <Tooltip 
                      contentStyle={{
                        backgroundColor: '#fff',
                        border: '1px solid #e5e7eb',
                        borderRadius: '6px',
                        fontFamily: 'sans-serif'
                      }}
                    />
                    <Legend 
                      wrapperStyle={{ fontFamily: 'sans-serif', fontSize: '12px' }}
                    />
                    <Bar dataKey="Cível" fill="#1A2B3C" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="Trab" fill="#4A5568" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-full text-gray-500">
                  <p>Nenhum dado disponível</p>
                </div>
              )}
            </div>
            <div className="flex items-center gap-4 mt-4 text-xs font-sans">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[#1A2B3C]"></div>
                <span className="text-gray-600">Cível</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[#4A5568]"></div>
                <span className="text-gray-600">Trab</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Gráfico de Linha - Produtividade */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-lg font-semibold text-[#1A2B3C] font-sans">
                  Produtividade Semestral
                </CardTitle>
                <p className="text-sm text-gray-600 font-sans mt-1">
                  Evolução de peticionamento e audiências
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm font-semibold text-[#1A2B3C] font-sans">Média: 140/mês</p>
                <p className="text-xs text-orange-600 font-sans">-2% variação sazonal</p>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              {dataProdutividade.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={dataProdutividade}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                    <XAxis 
                      dataKey="mes" 
                      tick={{ fill: '#6b7280', fontSize: 12 }}
                      style={{ fontFamily: 'sans-serif' }}
                    />
                    <YAxis 
                      tick={{ fill: '#6b7280', fontSize: 12 }}
                      style={{ fontFamily: 'sans-serif' }}
                    />
                    <Tooltip 
                      contentStyle={{
                        backgroundColor: '#fff',
                        border: '1px solid #e5e7eb',
                        borderRadius: '6px',
                        fontFamily: 'sans-serif'
                      }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="concluidos" 
                      stroke="#1A2B3C" 
                      strokeWidth={3} 
                      dot={{ r: 6, fill: '#1A2B3C' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-full text-gray-500">
                  <p>Nenhum dado disponível</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabelas e Listas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Alertas e Prazos Críticos */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg font-semibold text-[#1A2B3C] font-sans">
                Alertas e Prazos Críticos
              </CardTitle>
              <Button variant="ghost" size="sm" className="text-xs font-sans">
                Ver todos
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {criticalList.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="font-sans text-xs">ID PROCESSO</TableHead>
                    <TableHead className="font-sans text-xs">REQUERENTE</TableHead>
                    <TableHead className="font-sans text-xs">FASE</TableHead>
                    <TableHead className="font-sans text-xs">PRAZO FINAL</TableHead>
                    <TableHead className="font-sans text-xs">RISCO</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {criticalList.map((proc, idx) => {
                    const risk = calculateRisk(proc.daysUntil)
                    const processoId = proc.processo_adm_1doc || proc.processo_judicial || proc.protocol_number || `PROC-${idx}`
                    const requerente = proc.partes || proc.applicant_name || 'N/A'
                    const requerenteShort = requerente.length > 25 ? requerente.substring(0, 25) + '...' : requerente
                    
                    return (
                      <TableRow 
                        key={idx}
                        className="cursor-pointer hover:bg-gray-50"
                        onClick={() => {
                          const protocol = proc.protocol_number || processoId
                          if (protocol) {
                            navigate(`/process/${protocol}`)
                          }
                        }}
                      >
                        <TableCell className="font-sans text-xs font-mono">{processoId}</TableCell>
                        <TableCell className="font-sans text-xs">{requerenteShort}</TableCell>
                        <TableCell className="font-sans text-xs">Peticionamento</TableCell>
                        <TableCell className="font-sans text-xs">
                          {formatDeadline(proc.daysUntil)}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <div className={`w-2 h-2 rounded-full ${risk.color}`}></div>
                            <span className="text-xs font-sans">{risk.level}</span>
                          </div>
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            ) : (
              <div className="text-center py-8 text-gray-500 font-sans">
                <AlertCircle className="h-12 w-12 mx-auto mb-2 text-gray-400" />
                <p>Nenhum prazo crítico no momento</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Volume por Região */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-[#1A2B3C] font-sans">
              Volume por Região
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { name: 'SUDESTE', percent: 62 },
                { name: 'SUL', percent: 18 },
                { name: 'NORDESTE', percent: 12 },
                { name: 'CENTRO-OESTE', percent: 8 }
              ].map((regiao) => (
                <div key={regiao.name} className="space-y-2">
                  <div className="flex items-center justify-between text-sm font-sans">
                    <span className="font-medium text-gray-700">{regiao.name}</span>
                    <span className="font-semibold text-[#1A2B3C]">{regiao.percent}%</span>
                  </div>
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-[#1A2B3C] transition-all duration-300"
                      style={{ width: `${regiao.percent}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-6 pt-6 border-t border-gray-200">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-[#1A2B3C]/10 rounded-lg">
                  <FileText className="h-5 w-5 text-[#1A2B3C]" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-[#1A2B3C] font-sans">
                    COBERTURA NACIONAL
                  </p>
                  <p className="text-xs text-gray-600 font-sans">
                    24 filiais conectadas em tempo real
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
