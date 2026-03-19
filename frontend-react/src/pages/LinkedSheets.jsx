import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { 
  Link as LinkIcon, 
  RefreshCw, 
  Trash2, 
  CheckCircle, 
  AlertCircle, 
  Clock,
  ExternalLink,
  Activity
} from 'lucide-react'
import toast from 'react-hot-toast'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'

export default function LinkedSheets() {
  const queryClient = useQueryClient()
  const [refreshing, setRefreshing] = useState(null)

  // Buscar links monitorados
  const { data: linkedSheets = [], isLoading } = useQuery({
    queryKey: ['linked-sheets'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/sheets/linked`)
      return response.data
    },
  })

  // Mutation para desativar link
  const unlinkMutation = useMutation({
    mutationFn: async (fileId) => {
      const response = await axios.delete(`${API_URL}/api/sheets/link/${fileId}`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['linked-sheets'] })
      toast.success('Monitoramento desativado com sucesso')
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Erro ao desativar monitoramento')
    },
  })

  // Mutation para renovar watch channel
  const renewMutation = useMutation({
    mutationFn: async (fileId) => {
      const response = await axios.put(`${API_URL}/api/sheets/link/${fileId}/renew`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['linked-sheets'] })
      toast.success('Watch channel renovado com sucesso!')
      setRefreshing(null)
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Erro ao renovar watch channel')
      setRefreshing(null)
    },
  })

  const handleRenew = (fileId) => {
    setRefreshing(fileId)
    renewMutation.mutate(fileId)
  }

  // Função para verificar se está expirado
  const isExpired = (expiration) => {
    if (!expiration) return false
    return new Date(expiration) < new Date()
  }

  // Função para verificar se está próximo do vencimento (menos de 24h)
  const isExpiringSoon = (expiration) => {
    if (!expiration) return false
    const expDate = new Date(expiration)
    const now = new Date()
    const diffHours = (expDate.getTime() - now.getTime()) / (1000 * 60 * 60)
    return diffHours > 0 && diffHours < 24
  }

  // Função para formatar data
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  // Função para calcular tempo restante
  const getTimeRemaining = (expiration) => {
    if (!expiration) return 'N/A'
    const expDate = new Date(expiration)
    const now = new Date()
    const diffMs = expDate.getTime() - now.getTime()
    
    if (diffMs < 0) return 'Expirado'
    
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    const diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
    
    if (diffDays > 0) {
      return `${diffDays} dia(s) e ${diffHours} hora(s)`
    }
    return `${diffHours} hora(s)`
  }

  // Função para extrair file ID da URL
  const extractFileId = (url) => {
    const match = url.match(/\/d\/([a-zA-Z0-9-_]+)/)
    return match ? match[1] : null
  }

  const handleUnlink = (fileId) => {
    if (window.confirm('Tem certeza que deseja desativar o monitoramento desta planilha?')) {
      unlinkMutation.mutate(fileId)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Planilhas Monitoradas</h1>
          <p className="mt-2 text-gray-600">
            Gerencie as planilhas do Google Drive que estão sendo monitoradas automaticamente
          </p>
        </div>
        <Button
          onClick={() => queryClient.invalidateQueries({ queryKey: ['linked-sheets'] })}
          variant="outline"
          className="flex items-center space-x-2"
        >
          <RefreshCw className="h-4 w-4" />
          <span>Atualizar</span>
        </Button>
      </div>

      {linkedSheets.length === 0 ? (
        <Card className="p-12 text-center">
          <LinkIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Nenhuma planilha monitorada
          </h3>
          <p className="text-gray-600 mb-4">
            Quando você importar uma planilha do Google Drive com monitoramento automático ativado, 
            ela aparecerá aqui.
          </p>
        </Card>
      ) : (
        <Card>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>URL</TableHead>
                <TableHead>Última Sincronização</TableHead>
                <TableHead>Expiração</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {linkedSheets.map((sheet) => {
                const expired = isExpired(sheet.expiration)
                const expiringSoon = isExpiringSoon(sheet.expiration)
                const fileId = extractFileId(sheet.url)
                
                return (
                  <TableRow key={sheet.id}>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <LinkIcon className="h-4 w-4 text-gray-400" />
                        <a
                          href={sheet.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 underline text-sm flex items-center space-x-1"
                        >
                          <span className="truncate max-w-xs">
                            {sheet.url}
                          </span>
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        {sheet.last_sync ? (
                          <>
                            <Clock className="h-4 w-4 text-gray-400" />
                            <span className="text-sm text-gray-700">
                              {formatDate(sheet.last_sync)}
                            </span>
                          </>
                        ) : (
                          <span className="text-sm text-gray-400">Nunca sincronizado</span>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        {expired ? (
                          <>
                            <AlertCircle className="h-4 w-4 text-red-500" />
                            <span className="text-sm text-red-600 font-medium">Expirado</span>
                          </>
                        ) : expiringSoon ? (
                          <>
                            <AlertCircle className="h-4 w-4 text-yellow-500" />
                            <span className="text-sm text-yellow-600">
                              {getTimeRemaining(sheet.expiration)}
                            </span>
                          </>
                        ) : (
                          <>
                            <CheckCircle className="h-4 w-4 text-green-500" />
                            <span className="text-sm text-gray-700">
                              {getTimeRemaining(sheet.expiration)}
                            </span>
                          </>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      {expired ? (
                        <Badge variant="destructive">Expirado</Badge>
                      ) : expiringSoon ? (
                        <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-300">
                          Expirando em breve
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="bg-green-50 text-green-700 border-green-300">
                          <Activity className="h-3 w-3 mr-1" />
                          Ativo
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end space-x-2">
                        {(expired || expiringSoon) && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleRenew(sheet.file_id)}
                            disabled={refreshing === sheet.file_id || renewMutation.isPending}
                            className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                          >
                            {refreshing === sheet.file_id ? (
                              <>
                                <RefreshCw className="h-4 w-4 mr-1 animate-spin" />
                                Renovando...
                              </>
                            ) : (
                              <>
                                <RefreshCw className="h-4 w-4 mr-1" />
                                Renovar
                              </>
                            )}
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleUnlink(sheet.file_id)}
                          disabled={unlinkMutation.isPending}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 className="h-4 w-4 mr-1" />
                          Desativar
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </Card>
      )}

      {/* Informações sobre monitoramento */}
      <Card className="p-6 bg-blue-50 border-blue-200">
        <h3 className="text-lg font-semibold text-blue-900 mb-3 flex items-center space-x-2">
          <Activity className="h-5 w-5" />
          <span>Como funciona o monitoramento automático?</span>
        </h3>
        <ul className="space-y-2 text-sm text-blue-800">
          <li className="flex items-start space-x-2">
            <span className="font-semibold">•</span>
            <span>
              Quando você importa uma planilha do Google Drive com monitoramento ativado, 
              o sistema cria um "watch channel" que monitora alterações no arquivo.
            </span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="font-semibold">•</span>
            <span>
              Sempre que a planilha for modificada no Google Drive, o sistema recebe uma notificação 
              e sincroniza automaticamente os dados.
            </span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="font-semibold">•</span>
            <span>
              Os watch channels expiram após 7 dias. Quando estiver próximo do vencimento (menos de 24h), 
              o sistema tentará renová-lo automaticamente.
            </span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="font-semibold">•</span>
            <span>
              Apenas Google Sheets nativos suportam monitoramento dinâmico. Arquivos Excel/CSV são 
              convertidos automaticamente para Google Sheets durante o upload.
            </span>
          </li>
        </ul>
      </Card>
    </div>
  )
}
