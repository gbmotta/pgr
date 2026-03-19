import React, { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'

/**
 * Tabela Institucional - Padrão Jurídico
 * 
 * Características:
 * - Densidade informacional alta
 * - Alternância de cores nas linhas
 * - Header fixo ao scroll
 * - Hover states sutis
 * - Suporte a expansão de linhas
 */
export default function InstitutionalTable({ 
  columns, 
  data, 
  onRowClick,
  expandableContent,
  keyField = 'id'
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

  return (
    <div className="bg-white border border-neutral-border overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead className="bg-neutral-bg-tertiary sticky top-0 z-10">
            <tr>
              {expandableContent && (
                <th className="w-12 px-4 py-3 border-b border-neutral-border"></th>
              )}
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={`
                    px-4 py-3 text-left border-b border-neutral-border
                    text-xs font-semibold uppercase tracking-wide
                    text-neutral-text-primary
                    ${col.sortable ? 'cursor-pointer hover:bg-neutral-bg-secondary' : ''}
                  `}
                  onClick={() => col.sortable && handleSort(col.key)}
                >
                  <div className="flex items-center space-x-2">
                    <span>{col.label}</span>
                    {col.sortable && sortConfig.key === col.key && (
                      <span className="text-xs">
                        {sortConfig.direction === 'asc' ? '↑' : '↓'}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sortedData.length === 0 ? (
              <tr>
                <td
                  colSpan={columns.length + (expandableContent ? 1 : 0)}
                  className="px-4 py-12 text-center text-neutral-text-secondary"
                >
                  Nenhum registro encontrado
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
                        ${onRowClick ? 'cursor-pointer' : ''}
                        hover:bg-neutral-bg-tertiary
                      `}
                      onClick={() => onRowClick && onRowClick(row)}
                    >
                      {expandableContent && (
                        <td className="px-4 py-3">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              toggleRow(rowId)
                            }}
                            className="p-1 hover:bg-neutral-bg-tertiary rounded transition-colors"
                          >
                            {isExpanded ? (
                              <ChevronUp className="h-4 w-4 text-neutral-text-secondary" />
                            ) : (
                              <ChevronDown className="h-4 w-4 text-neutral-text-secondary" />
                            )}
                          </button>
                        </td>
                      )}
                      {columns.map((col) => (
                        <td
                          key={col.key}
                          className="px-4 py-3 text-sm text-neutral-text-primary"
                        >
                          {col.render ? col.render(row[col.key], row) : row[col.key]}
                        </td>
                      ))}
                    </tr>
                    {expandableContent && isExpanded && (
                      <tr>
                        <td
                          colSpan={columns.length + 1}
                          className="px-4 py-4 bg-neutral-bg-tertiary border-b border-neutral-border"
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
