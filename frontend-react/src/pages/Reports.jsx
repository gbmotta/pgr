import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import axios from 'axios'
import {
  Download,
  FileText,
  AlertTriangle,
  CalendarClock,
  Scale,
  LayoutList,
  Loader2,
  ExternalLink,
  Info,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { API_URL } from '@/lib/apiConfig'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { EmptyState } from '@/components/ui/empty-state'

function processHref(row) {
  const id = row.processo_adm_1doc || row.processo_judicial || row.protocol_number
  if (!id) return null
  return `/process/${encodeURIComponent(id)}`
}

export default function Reports() {
  const { data: stats, isLoading: loadingStats } = useQuery({
    queryKey: ['statistics'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/statistics/summary`)
      return res.data
    },
  })

  const { data: deadlineStatusData, isLoading: loadingSheetPrazos } = useQuery({
    queryKey: ['deadline-status-reports'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/processes/deadline-status`, {
        params: { alert_window_days: 30, include_ok: false },
      })
      return res.data
    },
  })

  const sheetAttentionRows =
    deadlineStatusData?.processes?.filter(
      (p) =>
        p.deadline_status?.status === 'overdue' || p.deadline_status?.status === 'upcoming'
    ) ?? []

  const { data: overdueLegal = [], isLoading: loadingOverdue } = useQuery({
    queryKey: ['overdue-deadlines'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/deadlines/overdue`)
      return res.data
    },
  })

  const { data: upcomingLegal = [], isLoading: loadingUpcoming } = useQuery({
    queryKey: ['upcoming-deadlines-reports'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/deadlines/upcoming`, { params: { days: 90 } })
      return res.data
    },
  })

  const loading = loadingStats || loadingSheetPrazos || loadingOverdue || loadingUpcoming

  const downloadReport = async (protocol) => {
    if (!protocol) {
      toast.error('Processo sem protocolo para o PDF.')
      return
    }
    try {
      const response = await axios.get(
        `${API_URL}/api/processes/${encodeURIComponent(protocol)}/report`,
        { responseType: 'blob' }
      )
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${protocol}_relatorio.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      toast.success('Relatório PDF descarregado.')
    } catch {
      toast.error('Erro ao gerar relatório.')
    }
  }

  const displayId = (row) =>
    row.processo_adm_1doc || row.processo_judicial || row.protocol_number || '—'

  return (
    <div className="mx-auto h-full max-w-6xl space-y-8 overflow-auto py-6">
      <section className="surface-panel px-6 py-6 lg:px-8">
        <span className="hero-badge">
          <FileText className="h-3.5 w-3.5" />
          Análise executiva
        </span>
        <h1 className="page-title mt-4">Relatórios</h1>
        <p className="page-subtitle mt-3">
          Resumo dos <strong>seus</strong> processos, prazos da planilha e prazos legais calculados no PGR.
        </p>
      </section>

      {loading && (
        <div className="flex items-center gap-2 text-gray-500 text-sm">
          <Loader2 className="h-5 w-5 animate-spin" />
          A carregar dados…
        </div>
      )}

      <Card className="border-[#d7e3ef] bg-[#eef5fb]/80 shadow-[0_12px_30px_-24px_rgba(37,99,235,0.45)]">
        <CardHeader className="pb-2">
          <CardTitle className="text-base flex items-center gap-2">
            <Info className="h-5 w-5 text-blue-700" />
            Legenda rápida
          </CardTitle>
          <CardDescription>Cores e tipos de prazo nesta página.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-gray-700">
          <span className="inline-flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-amber-600" />
            Prazo final da planilha (atenção)
          </span>
          <span className="inline-flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-red-600" />
            Prazo legal vencido
          </span>
          <span className="inline-flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-blue-700" />
            Prazo legal a vencer
          </span>
        </CardContent>
      </Card>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Processos na sua conta</CardDescription>
            <CardTitle className="text-2xl tabular-nums">
              {stats?.total_processes ?? '—'}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Prazo final (planilha) — crítico</CardDescription>
            <CardTitle className="text-2xl tabular-nums text-amber-700">
              {sheetAttentionRows.length}
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground pt-0">
            Vencidos ou nos próximos 30 dias (campo <em>prazo final</em>).
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Prazos legais vencidos</CardDescription>
            <CardTitle className="text-2xl tabular-nums text-red-700">
              {overdueLegal.length}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Prazos legais (90 dias)</CardDescription>
            <CardTitle className="text-2xl tabular-nums text-blue-700">
              {upcomingLegal.length}
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground pt-0">A vencer no prazo indicado.</CardContent>
        </Card>
      </div>

      <Card className="overflow-hidden border-[#d9dee6] shadow-[0_16px_34px_-28px_rgba(15,23,42,0.5)]">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-amber-600" />
            Prazo final da planilha — requer atenção
          </CardTitle>
          <CardDescription>
            Baseado no campo <strong>PRAZO FINAL (DD/MM)</strong> dos seus processos (janela de 30 dias).
          </CardDescription>
        </CardHeader>
        <CardContent>
          {sheetAttentionRows.length === 0 ? (
            <EmptyState
              compact
              title="Sem alertas de prazo final (planilha)"
              description="Nenhum processo com prazo final vencido ou nos próximos 30 dias, segundo os dados da sua conta."
            />
          ) : (
            <div className="soft-scrollbar overflow-x-auto rounded-2xl border border-[#dde2e8]">
              <table className="min-w-full text-sm">
                <thead className="bg-[#f6f3ee] text-left text-xs font-semibold uppercase tracking-wide text-slate-600">
                  <tr>
                    <th className="px-4 py-3">Processo</th>
                    <th className="px-4 py-3">Prazo final</th>
                    <th className="px-4 py-3">Situação</th>
                    <th className="px-4 py-3">Detalhe</th>
                    <th className="px-4 py-3 text-right">Ações</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {sheetAttentionRows.map((row) => {
                    const href = processHref(row)
                    const st = row.deadline_status
                    const overdue = st?.status === 'overdue'
                    const days = st?.days_until
                    return (
                      <tr key={row.id} className="hover:bg-[#f9f7f2]">
                        <td className="px-4 py-3 font-medium text-gray-900">{displayId(row)}</td>
                        <td className="px-4 py-3 text-gray-700">{row.prazo_final || '—'}</td>
                        <td className="px-4 py-3">
                          {overdue ? (
                            <span className="inline-flex rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-800">
                              Vencido
                            </span>
                          ) : (
                            <span className="inline-flex rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-900">
                              Próximo
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-gray-600 text-xs">
                          {overdue
                            ? `${days != null ? Math.abs(days) : '—'} dia(s) em atraso`
                            : `${days ?? '—'} dia(s) para vencer`}
                        </td>
                        <td className="px-4 py-3 text-right space-x-2 whitespace-nowrap">
                          {href && (
                            <Button variant="ghost" size="sm" asChild>
                              <Link to={href}>
                                <ExternalLink className="h-4 w-4" />
                              </Link>
                            </Button>
                          )}
                          <Button
                            variant="outline"
                            size="sm"
                            type="button"
                            onClick={() => downloadReport(row.protocol_number || displayId(row))}
                          >
                            <FileText className="h-4 w-4" />
                          </Button>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="overflow-hidden border-[#d9dee6] shadow-[0_16px_34px_-28px_rgba(15,23,42,0.5)]">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Scale className="h-5 w-5 text-red-600" />
            Prazos legais vencidos
          </CardTitle>
          <CardDescription>
            Instâncias de prazos legais (checklist do tipo de processo) ainda em aberto e com data passada.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {overdueLegal.length === 0 ? (
            <EmptyState
              compact
              title="Sem prazos legais vencidos"
              description="Quando existirem prazos legais em atraso, aparecem aqui com link para o processo e opção de PDF."
            />
          ) : (
            <div className="soft-scrollbar overflow-x-auto rounded-2xl border border-[#dde2e8]">
              <table className="min-w-full text-sm">
                <thead className="bg-[#f6f3ee] text-left text-xs font-semibold uppercase tracking-wide text-slate-600">
                  <tr>
                    <th className="px-4 py-3">Protocolo</th>
                    <th className="px-4 py-3">Tipo</th>
                    <th className="px-4 py-3">Prazo</th>
                    <th className="px-4 py-3">Vencimento</th>
                    <th className="px-4 py-3">Atraso</th>
                    <th className="px-4 py-3 text-right">Ações</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {overdueLegal.map((deadline, idx) => (
                    <tr key={idx} className="hover:bg-[#f9f7f2]">
                      <td className="px-4 py-3 font-medium">
                        {deadline.protocol_number || '—'}
                      </td>
                      <td className="px-4 py-3 text-gray-600">{deadline.type_name || '—'}</td>
                      <td className="px-4 py-3 text-gray-700">{deadline.deadline_name}</td>
                      <td className="px-4 py-3">
                        {deadline.due_date
                          ? new Date(deadline.due_date).toLocaleDateString('pt-BR')
                          : '—'}
                      </td>
                      <td className="px-4 py-3 font-medium text-red-600">
                        {deadline.days_overdue} dia(s)
                      </td>
                      <td className="px-4 py-3 text-right whitespace-nowrap space-x-2">
                        {deadline.protocol_number && (
                          <>
                            <Button variant="ghost" size="sm" asChild>
                              <Link to={`/process/${encodeURIComponent(deadline.protocol_number)}`}>
                                <ExternalLink className="h-4 w-4" />
                              </Link>
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              type="button"
                              onClick={() => downloadReport(deadline.protocol_number)}
                            >
                              <Download className="h-4 w-4" />
                            </Button>
                          </>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <CalendarClock className="h-5 w-5 text-blue-600" />
            Prazos legais a vencer (90 dias)
          </CardTitle>
          <CardDescription>Próximos vencimentos de prazos legais associados aos seus processos.</CardDescription>
        </CardHeader>
        <CardContent>
          {upcomingLegal.length === 0 ? (
            <EmptyState
              compact
              title="Sem prazos legais neste período"
              description="Não há prazos legais a vencer nos próximos 90 dias para os seus processos."
            />
          ) : (
            <div className="overflow-x-auto rounded-md border">
              <table className="min-w-full text-sm">
                <thead className="bg-slate-50 text-left text-xs font-semibold text-slate-600 uppercase tracking-wide">
                  <tr>
                    <th className="px-4 py-3">Protocolo</th>
                    <th className="px-4 py-3">Tipo</th>
                    <th className="px-4 py-3">Prazo</th>
                    <th className="px-4 py-3">Vencimento</th>
                    <th className="px-4 py-3">Dias</th>
                    <th className="px-4 py-3 text-right">Ações</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {upcomingLegal.map((d, idx) => (
                    <tr key={idx} className="hover:bg-slate-50/80">
                      <td className="px-4 py-3 font-medium">{d.protocol_number || '—'}</td>
                      <td className="px-4 py-3 text-gray-600">{d.type_name || '—'}</td>
                      <td className="px-4 py-3 text-gray-700">{d.deadline_name}</td>
                      <td className="px-4 py-3">
                        {d.due_date ? new Date(d.due_date).toLocaleDateString('pt-BR') : '—'}
                      </td>
                      <td className="px-4 py-3 text-blue-700">{d.days_remaining} dia(s)</td>
                      <td className="px-4 py-3 text-right whitespace-nowrap space-x-2">
                        {d.protocol_number && (
                          <>
                            <Button variant="ghost" size="sm" asChild>
                              <Link to={`/process/${encodeURIComponent(d.protocol_number)}`}>
                                <ExternalLink className="h-4 w-4" />
                              </Link>
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              type="button"
                              onClick={() => downloadReport(d.protocol_number)}
                            >
                              <Download className="h-4 w-4" />
                            </Button>
                          </>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="border-dashed border-[#d5dbe4] bg-[#fcfbf8]">
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <LayoutList className="h-5 w-5 text-gray-500" />
            Dica
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-gray-600">
          Os dados desta página respeitam a sua conta. Para introduzir ou alterar processos, use{' '}
          <Link to="/upload" className="text-blue-600 font-medium hover:underline">
            Upload
          </Link>{' '}
          (planilha no PGR, ficheiro ou Google). O{' '}
          <Link to="/calendar" className="text-blue-600 font-medium hover:underline">
            Calendário
          </Link>{' '}
          mostra os mesmos prazos numa vista mensal.
        </CardContent>
      </Card>
    </div>
  )
}
