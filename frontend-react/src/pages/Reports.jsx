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
} from 'lucide-react'
import toast from 'react-hot-toast'
import { API_URL } from '@/lib/apiConfig'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

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
    <div className="h-full px-4 sm:px-6 lg:px-8 py-6 overflow-auto max-w-6xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Relatórios</h1>
        <p className="mt-2 text-gray-600">
          Resumo dos <strong>seus</strong> processos, prazos da planilha e prazos legais calculados no PGR.
        </p>
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-gray-500 text-sm">
          <Loader2 className="h-5 w-5 animate-spin" />
          A carregar dados…
        </div>
      )}

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

      <Card>
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
            <p className="text-sm text-gray-500">
              Nenhum processo com prazo final vencido ou próximo nos próximos 30 dias.
            </p>
          ) : (
            <div className="overflow-x-auto rounded-md border">
              <table className="min-w-full text-sm">
                <thead className="bg-slate-50 text-left text-xs font-semibold text-slate-600 uppercase tracking-wide">
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
                      <tr key={row.id} className="hover:bg-slate-50/80">
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

      <Card>
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
            <p className="text-sm text-gray-500">Nenhum prazo legal vencido encontrado.</p>
          ) : (
            <div className="overflow-x-auto rounded-md border">
              <table className="min-w-full text-sm">
                <thead className="bg-slate-50 text-left text-xs font-semibold text-slate-600 uppercase tracking-wide">
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
                    <tr key={idx} className="hover:bg-slate-50/80">
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
            <p className="text-sm text-gray-500">Nenhum prazo legal neste intervalo.</p>
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

      <Card className="border-dashed">
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
