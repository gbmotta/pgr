import React from 'react'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Card, CardContent } from "@/components/ui/card"

/**
 * Tabela de Processos
 * 
 * Componente que exibe uma tabela de processos administrativos com:
 * - Colunas: Processo, Partes, Prazo Final, Status
 * - Cores dinâmicas baseadas no prazo
 * - Design limpo e profissional
 */
export default function ProcessTable({ 
  data = [],
  onRowClick 
}) {
  /**
   * Calcula o status do prazo baseado na data
   * 
   * @param {string|Date} deadlineDate - Data do prazo (pode ser string DD/MM ou Date)
   * @returns {object} Objeto com status, label, classes CSS e dias restantes
   */
  const getDeadlineStatus = (deadlineDate) => {
    if (!deadlineDate) {
      return {
        status: 'sem-prazo',
        label: 'Sem prazo',
        bgClass: 'bg-gray-100',
        textClass: 'text-gray-700',
        daysUntil: null
      }
    }

    let prazoDate

    // Se for string no formato DD/MM
    if (typeof deadlineDate === 'string' && deadlineDate.includes('/')) {
      const [day, month] = deadlineDate.split('/').map(Number)
      if (!day || !month || isNaN(day) || isNaN(month)) {
        return {
          status: 'invalido',
          label: 'Data inválida',
          bgClass: 'bg-gray-100',
          textClass: 'text-gray-700',
          daysUntil: null
        }
      }

      const now = new Date()
      const year = now.getFullYear()
      prazoDate = new Date(year, month - 1, day)

      // Se a data já passou neste ano, considerar próximo ano
      if (prazoDate < now) {
        prazoDate.setFullYear(year + 1)
      }
    } else if (deadlineDate instanceof Date) {
      prazoDate = new Date(deadlineDate)
    } else {
      // Tentar converter string para Date
      prazoDate = new Date(deadlineDate)
      if (isNaN(prazoDate.getTime())) {
        return {
          status: 'invalido',
          label: 'Data inválida',
          bgClass: 'bg-gray-100',
          textClass: 'text-gray-700',
          daysUntil: null
        }
      }
    }

    const now = new Date()
    const daysUntil = Math.ceil((prazoDate - now) / (1000 * 60 * 60 * 24))

    // Se a data já passou
    if (daysUntil < 0) {
      return {
        status: 'vencido',
        label: 'Vencido',
        bgClass: 'bg-red-100', // Vermelho Sóbrio (Slate Red) - fundo
        textClass: 'text-red-800', // Vermelho Sóbrio para texto
        borderClass: 'border-red-300',
        daysUntil
      }
    }

    // Se faltarem menos de 7 dias
    if (daysUntil < 7) {
      return {
        status: 'urgente',
        label: 'Urgente',
        bgClass: 'bg-yellow-100', // Amarelo Mostarda - fundo
        textClass: 'text-yellow-900', // Amarelo Mostarda para texto
        borderClass: 'border-yellow-300',
        daysUntil
      }
    }

    // Se faltarem mais de 7 dias
    return {
      status: 'no-prazo',
      label: 'No Prazo',
      bgClass: 'bg-green-100', // Verde Sage - fundo
      textClass: 'text-green-800', // Verde Sage para texto
      borderClass: 'border-green-300',
      daysUntil
    }
  }

  /**
   * Formata a data para exibição
   */
  const formatDate = (date) => {
    if (!date) return '-'
    
    if (typeof date === 'string' && date.includes('/')) {
      return date // Já está no formato DD/MM
    }
    
    if (date instanceof Date) {
      const day = String(date.getDate()).padStart(2, '0')
      const month = String(date.getMonth() + 1).padStart(2, '0')
      return `${day}/${month}`
    }
    
    return String(date)
  }

  // Se não houver dados, exibir mensagem
  if (!data || data.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <p className="text-muted-foreground font-sans">Nenhum processo encontrado</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="font-sans">Processo</TableHead>
            <TableHead className="font-sans">Partes</TableHead>
            <TableHead className="font-sans">Prazo Final</TableHead>
            <TableHead className="font-sans">Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map((processo, index) => {
            const deadlineStatus = getDeadlineStatus(processo.prazo_final)
            
            return (
              <TableRow
                key={processo.id || index}
                onClick={() => onRowClick && onRowClick(processo)}
                className={onRowClick ? 'cursor-pointer' : ''}
              >
                <TableCell className="font-sans">
                  {processo.processo || processo.processo_adm_1doc || processo.numero || '-'}
                </TableCell>
                <TableCell className="font-sans max-w-md truncate">
                  {processo.partes || '-'}
                </TableCell>
                <TableCell className="font-sans">
                  {formatDate(processo.prazo_final)}
                </TableCell>
                <TableCell>
                  <span
                    className={`
                      inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold
                      ${deadlineStatus.bgClass}
                      ${deadlineStatus.textClass}
                      border ${deadlineStatus.borderClass || 'border-transparent'}
                      font-sans
                    `}
                  >
                    {deadlineStatus.label}
                    {deadlineStatus.daysUntil !== null && deadlineStatus.daysUntil >= 0 && (
                      <span className="ml-1 text-xs opacity-75">
                        ({deadlineStatus.daysUntil} {deadlineStatus.daysUntil === 1 ? 'dia' : 'dias'})
                      </span>
                    )}
                  </span>
                </TableCell>
              </TableRow>
            )
          })}
        </TableBody>
      </Table>
    </Card>
  )
}
