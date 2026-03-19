import React, { useState } from 'react'
import { ChevronDown, ChevronUp, Clock, AlertCircle, CheckCircle } from 'lucide-react'

/**
 * Tabela Densa Jurídica - Processos Administrativos
 * 
 * Características:
 * - Layout full-width
 * - Ordem exata das colunas conforme schema canônico
 * - Tabela scrollable
 * - Flags visuais para prazos e status
 * - Design profissional jurídico (não SaaS)
 * - Alta densidade informacional
 */
export default function LegalProcessTable({ 
  data, 
  onRowClick,
  expandableContent,
  keyField = 'id',
  alertWindowDays = 7
}) {
  const [expandedRows, setExpandedRows] = useState(new Set())
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' })

  const toggleRow = (rowId) => {
    const newExpanded = new Set(expandedRows)
    if (newExpanded.has(rowId)) {
      newExpanded.delete(rowId)
    } else {
      newExpanded.add(rowId)
    }
    setExpandedRows(newExpanded)
  }

  const handleSort = (key) => {
    let direction = 'asc'
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc'
    }
    setSortConfig({ key, direction })
  }

  const sortedData = [...data].sort((a, b) => {
    if (!sortConfig.key) return 0
    
    const aVal = a[sortConfig.key]
    const bVal = b[sortConfig.key]
    
    if (aVal === null || aVal === undefined) return 1
    if (bVal === null || bVal === undefined) return -1
    
    if (typeof aVal === 'string') {
      return sortConfig.direction === 'asc'
        ? aVal.localeCompare(bVal)
        : bVal.localeCompare(aVal)
    }
    
    return sortConfig.direction === 'asc' ? aVal - bVal : bVal - aVal
  })

  const getPrazoStatus = (prazoStr) => {
    if (!prazoStr) return null
    const [day, month] = prazoStr.split('/').map(Number)
    if (!day || !month) return null
    
    const now = new Date()
    const year = now.getFullYear()
    let prazoDate = new Date(year, month - 1, day)
    
    if (prazoDate < now) {
      prazoDate.setFullYear(year + 1)
    }
    
    const daysUntil = Math.ceil((prazoDate - now) / (1000 * 60 * 60 * 24))
    
    if (daysUntil < 0) return { status: 'vencido', color: 'text-status-vencido', bg: 'bg-status-vencido/10', icon: AlertCircle, daysUntil }
    if (daysUntil <= 7) return { status: 'vencendo', color: 'text-status-indeferido', bg: 'bg-status-indeferido/10', icon: Clock, daysUntil }
    if (daysUntil <= 30) return { status: 'atencao', color: 'text-status-em-analise', bg: 'bg-status-em-analise/10', icon: Clock, daysUntil }
    return { status: 'ok', color: 'text-status-deferido', bg: 'bg-status-deferido/10', icon: CheckCircle, daysUntil }
  }

  const getRowDeadlineClass = (row) => {
    const status = getPrazoStatus(row.prazo_final)
    if (!status) return ''
    
    if (status.status === 'vencido') {
      return 'border-l-4 border-status-vencido bg-status-vencido/5'
    } else if (status.status === 'vencendo') {
      return 'border-l-4 border-status-indeferido bg-status-indeferido/5'
    } else if (status.status === 'atencao' && status.daysUntil <= alertWindowDays) {
      return 'border-l-4 border-status-em-analise bg-status-em-analise/5'
    }
    return ''
  }

  // Ordem canônica exata conforme schema
  const canonicalColumns = [
    {
      key: 'processo_adm_1doc',
      label: 'PROCESSO ADM 1DOC',
      sortable: true,
      width: 'w-48',
      render: (value, row) => {
        if (!value && !row.processo_judicial) {
          return <span className="text-neutral-text-tertiary italic text-xs">—</span>
        }
        return (
          <div className="font-mono text-sm font-semibold text-neutral-text-primary">
            {value || '—'}
          </div>
        )
      }
    },
    {
      key: 'processo_judicial',
      label: 'PROCESSO JUDICIAL',
      sortable: true,
      width: 'w-48',
      render: (value) => {
        if (!value) return <span className="text-neutral-text-tertiary italic text-xs">—</span>
        return <span className="font-mono text-sm font-semibold text-neutral-text-primary">{value}</span>
      }
    },
    {
      key: 'partes',
      label: 'PARTES',
      sortable: false,
      width: 'w-64',
      render: (value) => {
        if (!value) return <span className="text-neutral-text-tertiary italic text-xs">—</span>
        const truncated = value.length > 60 ? value.substring(0, 60) + '...' : value
        return <span className="text-xs text-neutral-text-primary leading-relaxed">{truncated}</span>
      }
    },
    {
      key: 'data_recebimento_mes_ano',
      label: 'DATA RECEBIMENTO (MÊS/ANO)',
      sortable: true,
      width: 'w-40',
      render: (value) => {
        if (!value) return <span className="text-neutral-text-tertiary italic text-xs">—</span>
        return <span className="text-xs font-mono text-neutral-text-primary">{value}</span>
      }
    },
    {
      key: 'tema_observacoes',
      label: 'TEMA – OBSERVAÇÕES',
      sortable: false,
      width: 'w-80',
      render: (value) => {
        if (!value) return <span className="text-neutral-text-tertiary italic text-xs">—</span>
        const truncated = value.length > 80 ? value.substring(0, 80) + '...' : value
        return <span className="text-xs text-neutral-text-primary leading-relaxed">{truncated}</span>
      }
    },
    {
      key: 'prazo_info_estag',
      label: 'PRAZO INFO – ESTAG (DIA/MÊS)',
      sortable: false,
      width: 'w-44',
      render: (value) => {
        if (!value) return <span className="text-neutral-text-tertiary italic text-xs">—</span>
        return (
          <div className="flex items-center space-x-1.5">
            <Clock className="h-3.5 w-3.5 text-neutral-text-tertiary" />
            <span className="text-xs font-mono text-neutral-text-primary">{value}</span>
          </div>
        )
      }
    },
    {
      key: 'prazo_final',
      label: 'PRAZO FINAL (DD/MM)',
      sortable: true,
      width: 'w-36',
      render: (value) => {
        if (!value) return <span className="text-neutral-text-tertiary italic text-xs">—</span>
        const prazoStatus = getPrazoStatus(value)
        if (!prazoStatus) {
          return <span className="text-xs font-mono text-neutral-text-primary">{value}</span>
        }
        const Icon = prazoStatus.icon
        return (
          <div className={`inline-flex items-center space-x-1.5 px-2 py-1 rounded ${prazoStatus.bg} ${prazoStatus.color}`}>
            <Icon className="h-3.5 w-3.5" />
            <span className="text-xs font-mono font-semibold">{value}</span>
          </div>
        )
      }
    },
    {
      key: 'tipo_ato',
      label: 'TIPO DE ATO',
      sortable: true,
      width: 'w-40',
      render: (value) => {
        if (!value) return <span className="text-neutral-text-tertiary italic text-xs">—</span>
        return <span className="text-xs text-neutral-text-primary">{value}</span>
      }
    },
    {
      key: 'data_realizacao_ato',
      label: 'DATA DE REALIZAÇÃO DO ATO (DD/MM/YYYY)',
      sortable: true,
      width: 'w-48',
      render: (value) => {
        if (!value) return <span className="text-neutral-text-tertiary italic text-xs">—</span>
        return <span className="text-xs font-mono text-neutral-text-primary">{value}</span>
      }
    }
  ]

  return (
    <div className="w-full bg-white border border-neutral-border">
      <div className="overflow-x-auto overflow-y-auto max-h-[calc(100vh-300px)]">
        <table className="w-full border-collapse min-w-full">
          <thead className="bg-neutral-bg-tertiary sticky top-0 z-20 border-b-2 border-neutral-border">
            <tr>
              {expandableContent && (
                <th className="w-10 px-3 py-2.5 border-r border-neutral-border"></th>
              )}
              {canonicalColumns.map((col) => (
                <th
                  key={col.key}
                  className={`
                    ${col.width || ''}
                    px-3 py-2.5 text-left border-r border-neutral-border
                    text-[10px] font-bold uppercase tracking-wider
                    text-neutral-text-primary
                    ${col.sortable ? 'cursor-pointer hover:bg-neutral-bg-secondary select-none' : ''}
                  `}
                  onClick={() => col.sortable && handleSort(col.key)}
                >
                  <div className="flex items-center space-x-1.5">
                    <span className="leading-tight">{col.label}</span>
                    {col.sortable && sortConfig.key === col.key && (
                      <span className="text-[10px] font-normal">
                        {sortConfig.direction === 'asc' ? '↑' : '↓'}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-border-light">
            {sortedData.length === 0 ? (
              <tr>
                <td
                  colSpan={canonicalColumns.length + (expandableContent ? 1 : 0)}
                  className="px-4 py-16 text-center text-neutral-text-secondary text-sm"
                >
                  Nenhum processo encontrado
                </td>
              </tr>
            ) : (
              sortedData.map((row, index) => {
                const rowId = row[keyField]
                const isExpanded = expandedRows.has(rowId)
                const isEven = index % 2 === 0

                return (
                  <React.Fragment key={rowId}>
                    <tr
                      className={`
                        border-b border-neutral-border-light transition-colors
                        ${isEven ? 'bg-white' : 'bg-neutral-bg-secondary'}
                        ${onRowClick ? 'cursor-pointer hover:bg-neutral-bg-tertiary' : ''}
                        ${getRowDeadlineClass(row)}
                      `}
                      onClick={() => onRowClick && onRowClick(row)}
                    >
                      {expandableContent && (
                        <td className="px-3 py-2 border-r border-neutral-border-light">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              toggleRow(rowId)
                            }}
                            className="p-0.5 hover:bg-neutral-bg-tertiary rounded transition-colors"
                            aria-label={isExpanded ? 'Recolher' : 'Expandir'}
                          >
                            {isExpanded ? (
                              <ChevronUp className="h-3.5 w-3.5 text-neutral-text-secondary" />
                            ) : (
                              <ChevronDown className="h-3.5 w-3.5 text-neutral-text-secondary" />
                            )}
                          </button>
                        </td>
                      )}
                      {canonicalColumns.map((col) => (
                        <td
                          key={col.key}
                          className={`
                            ${col.width || ''}
                            px-3 py-2 border-r border-neutral-border-light
                            text-xs text-neutral-text-primary
                            align-top
                          `}
                        >
                          {col.render ? col.render(row[col.key], row) : (row[col.key] || <span className="text-neutral-text-tertiary italic">—</span>)}
                        </td>
                      ))}
                    </tr>
                    {expandableContent && isExpanded && (
                      <tr className="bg-neutral-bg-tertiary">
                        <td
                          colSpan={canonicalColumns.length + 1}
                          className="px-6 py-4 border-b border-neutral-border"
                        >
                          {expandableContent(row)}
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                )
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
