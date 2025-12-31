import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { 
  ArrowLeft, 
  Download, 
  Upload as UploadIcon,
  CheckCircle,
  XCircle,
  Calendar,
  FileText
} from 'lucide-react'
import { useState } from 'react'
import toast from 'react-hot-toast'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function ProcessDetail() {
  const { protocol } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [uploading, setUploading] = useState(false)

  const { data: process, isLoading } = useQuery({
    queryKey: ['process', protocol],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/processes/${protocol}`)
      return response.data
    },
  })

  const { data: attachments } = useQuery({
    queryKey: ['attachments', protocol],
    queryFn: async () => {
      try {
        const response = await axios.get(`${API_URL}/api/processes/${protocol}/attachments`)
        return response.data
      } catch {
        return []
      }
    },
  })

  const downloadReport = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/api/processes/${protocol}/report`,
        { responseType: 'blob' }
      )
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${protocol}_relatorio.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      toast.success('Relatório gerado com sucesso!')
    } catch (error) {
      toast.error('Erro ao gerar relatório')
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      await axios.post(`${API_URL}/api/processes/${protocol}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      toast.success('Documento enviado com sucesso!')
      queryClient.invalidateQueries(['attachments', protocol])
      queryClient.invalidateQueries(['process', protocol])
    } catch (error) {
      toast.error('Erro ao enviar documento')
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!process) {
    return <div>Processo não encontrado</div>
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="mb-6">
        <button
          onClick={() => navigate('/dashboard')}
          className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 mb-4"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Voltar
        </button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{process.protocol_number}</h1>
            <p className="mt-2 text-gray-600">{process.applicant_name}</p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={downloadReport}
              className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <Download className="mr-2 h-4 w-4" />
              Gerar PDF
            </button>
            <label className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 cursor-pointer">
              <UploadIcon className="mr-2 h-4 w-4" />
              {uploading ? 'Enviando...' : 'Enviar Documento'}
              <input
                type="file"
                className="hidden"
                onChange={handleFileUpload}
                disabled={uploading}
              />
            </label>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Informações principais */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Informações do Processo</h2>
            <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <dt className="text-sm font-medium text-gray-500">Tipo</dt>
                <dd className="mt-1 text-sm text-gray-900">{process.type?.name || process.type_name}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Status</dt>
                <dd className="mt-1 text-sm text-gray-900">{process.status?.label || process.status_code}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Data de Criação</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {format(new Date(process.created_date), "dd 'de' MMMM 'de' yyyy", { locale: ptBR })}
                </dd>
              </div>
              {process.applicant_registration && (
                <div>
                  <dt className="text-sm font-medium text-gray-500">Matrícula</dt>
                  <dd className="mt-1 text-sm text-gray-900">{process.applicant_registration}</dd>
                </div>
              )}
            </dl>
            {process.parecer && (
              <div className="mt-4">
                <dt className="text-sm font-medium text-gray-500">Parecer</dt>
                <dd className="mt-1 text-sm text-gray-900">{process.parecer}</dd>
              </div>
            )}
          </div>

          {/* Documentos */}
          {process.documents && process.documents.length > 0 && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Documentos</h2>
              <div className="space-y-3">
                {process.documents.map((doc, idx) => (
                  <div
                    key={idx}
                    className={`flex items-center justify-between p-3 rounded-lg ${
                      doc.provided ? 'bg-green-50' : 'bg-red-50'
                    }`}
                  >
                    <div className="flex items-center">
                      {doc.provided ? (
                        <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                      ) : (
                        <XCircle className="h-5 w-5 text-red-500 mr-3" />
                      )}
                      <div>
                        <div className="text-sm font-medium text-gray-900">{doc.name}</div>
                        {doc.provided_date && (
                          <div className="text-xs text-gray-500">
                            Fornecido em: {format(new Date(doc.provided_date), 'dd/MM/yyyy')}
                          </div>
                        )}
                      </div>
                    </div>
                    {doc.required && (
                      <span className="text-xs text-red-600 font-medium">Obrigatório</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Prazos */}
          {process.deadlines && process.deadlines.length > 0 && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Prazos</h2>
              <div className="space-y-3">
                {process.deadlines.map((deadline, idx) => {
                  const isOverdue = new Date(deadline.due_date) < new Date() && !deadline.closed
                  return (
                    <div
                      key={idx}
                      className={`flex items-center justify-between p-3 rounded-lg ${
                        isOverdue ? 'bg-red-50' : deadline.closed ? 'bg-green-50' : 'bg-yellow-50'
                      }`}
                    >
                      <div className="flex items-center">
                        <Calendar className="h-5 w-5 text-gray-400 mr-3" />
                        <div>
                          <div className="text-sm font-medium text-gray-900">{deadline.name}</div>
                          <div className="text-xs text-gray-500">
                            {format(new Date(deadline.due_date), "dd 'de' MMMM 'de' yyyy", {
                              locale: ptBR,
                            })}
                          </div>
                        </div>
                      </div>
                      {deadline.closed ? (
                        <span className="text-xs text-green-600 font-medium">Cumprido</span>
                      ) : isOverdue ? (
                        <span className="text-xs text-red-600 font-medium">Vencido</span>
                      ) : (
                        <span className="text-xs text-yellow-600 font-medium">Pendente</span>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>

        {/* Anexos */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Anexos</h2>
          {attachments && attachments.length > 0 ? (
            <div className="space-y-2">
              {attachments.map((attachment) => (
                <a
                  key={attachment.id}
                  href={`${API_URL}${attachment.download_url}`}
                  className="flex items-center p-2 rounded hover:bg-gray-50"
                >
                  <FileText className="h-4 w-4 text-gray-400 mr-2" />
                  <span className="text-sm text-gray-900 truncate">{attachment.original_filename}</span>
                </a>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500">Nenhum anexo</p>
          )}
        </div>
      </div>
    </div>
  )
}

