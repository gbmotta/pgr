import { useState, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import axios from 'axios'
import { Upload, FileSpreadsheet, Link as LinkIcon, FileUp, Eye, AlertCircle, CheckCircle, X } from 'lucide-react'
import toast from 'react-hot-toast'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'

export default function UploadProcesses() {
  const [file, setFile] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [googleDriveLink, setGoogleDriveLink] = useState('')
  const [uploadMode, setUploadMode] = useState('file')
  const [previewData, setPreviewData] = useState(null)
  const [showPreview, setShowPreview] = useState(false)
  const [serviceAccountEmail, setServiceAccountEmail] = useState(null)
  const [loadingEmail, setLoadingEmail] = useState(false)
  const [enableAutoSync, setEnableAutoSync] = useState(true) // Monitoramento automático ativado por padrão

  const previewMutation = useMutation({
    mutationFn: async (file) => {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await axios.post(`${API_URL}/api/processes/preview-upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        params: { preview_rows: 20 }
      })
      return response.data
    },
    onSuccess: (data) => {
      setPreviewData(data)
      setShowPreview(true)
      if (data.can_import) {
        toast.success(`✅ Preview gerado: ${data.summary.valid} linha(s) válida(s)`)
      } else {
        toast.error(`❌ ${data.summary.errors} erro(s) crítico(s) encontrado(s)`)
      }
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Erro ao gerar preview')
    },
  })

  const uploadFileMutation = useMutation({
    mutationFn: async (file) => {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await axios.post(`${API_URL}/processes/upload-excel`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return response.data
    },
    onSuccess: (data) => {
      const imported = data.imported || 0
      const skipped = data.skipped || 0
      if (imported > 0) {
        toast.success(`✅ ${imported} processo(s) importado(s)${skipped > 0 ? `, ${skipped} já existiam` : ''}`)
      } else if (skipped > 0) {
        toast.info(`ℹ️ ${skipped} processo(s) já existem no banco. Nenhum novo processo importado.`)
      } else {
        toast('Nenhum processo foi importado.', {
          icon: 'ℹ️',
          style: {
            background: '#3b82f6',
            color: '#fff',
          }
        })
      }
      setFile(null)
      setPreviewData(null)
      setShowPreview(false)
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Erro ao importar processos')
    },
  })

  const previewGoogleDriveMutation = useMutation({
    mutationFn: async (url) => {
      const response = await axios.post(`${API_URL}/api/processes/preview-google-sheets`, {
        url: url,
      }, {
        params: { preview_rows: 20 }
      })
      return response.data
    },
    onSuccess: (data) => {
      setPreviewData(data)
      setShowPreview(true)
      
      // Mostrar aviso se houve problema na conversão mas continuou
      if (data.conversion_warning) {
        const warningMsg = typeof data.conversion_warning === 'string' 
          ? data.conversion_warning.split('\n').slice(0, 3).join(' ')
          : 'Aviso: Não foi possível converter para Google Sheets, mas a importação continuará.'
        toast(warningMsg, { 
          duration: 8000,
          icon: '⚠️',
          style: {
            background: '#fbbf24',
            color: '#1f2937',
          }
        })
      }
      
      if (data.can_import) {
        toast.success(`✅ Preview gerado: ${data.summary.valid} linha(s) válida(s)`)
      } else {
        toast.error(`❌ ${data.summary.errors} erro(s) crítico(s) encontrado(s)`)
      }
    },
    onError: (error) => {
      const errorDetail = error.response?.data?.detail
      
      // Se for um objeto com mensagem estruturada
      if (typeof errorDetail === 'object' && errorDetail.message) {
        // Mostrar mensagem completa (pode conter instruções de conversão)
        const fullMessage = errorDetail.message
        // Se a mensagem for muito longa, mostrar em múltiplas linhas ou truncar
        if (fullMessage.length > 200) {
          // Mostrar primeiras linhas importantes
          const lines = fullMessage.split('\n')
          const importantLines = lines.slice(0, 4).join('\n')
          toast.error(importantLines, { duration: 8000 })
        } else {
          toast.error(fullMessage, { duration: 6000 })
        }
      } else if (typeof errorDetail === 'string') {
        // Se for string direta
        toast.error(errorDetail, { duration: 6000 })
      } else {
        toast.error(error.message || 'Erro ao gerar preview do Google Sheets')
      }
    },
  })

  const uploadGoogleDriveMutation = useMutation({
    mutationFn: async (url) => {
      const response = await axios.post(`${API_URL}/processes/upload-from-google-drive`, {
        url: url,
      })
      return response.data
    },
    onSuccess: async (data) => {
      const imported = data.imported || 0
      const skipped = data.skipped || 0
      
      // Mostrar aviso se houve problema na conversão mas continuou
      if (data.conversion_warning) {
        const warningMsg = typeof data.conversion_warning === 'string' 
          ? data.conversion_warning.split('\n').slice(0, 3).join(' ')
          : 'Aviso: Não foi possível converter para Google Sheets, mas a importação continuou.'
        toast(warningMsg, { 
          duration: 8000,
          icon: '⚠️',
          style: {
            background: '#fbbf24',
            color: '#1f2937',
          }
        })
      }
      
      // Se o monitoramento automático estiver ativado e o arquivo pode ser monitorado, criar watch channel
      if (enableAutoSync && data.can_monitor) {
        try {
          // Usar o file_id retornado pelo backend (pode ser o Google Sheets criado após conversão)
          const urlToLink = data.google_sheets_url || googleDriveLink
          
          const linkResponse = await axios.post(`${API_URL}/api/sheets/link`, {
            url: urlToLink,
          })
          
          if (linkResponse.data?.status === 'linked') {
            const convertedMsg = data.converted_to_sheets 
              ? '\n📝 Arquivo convertido para Google Sheets nativo para permitir monitoramento.'
              : ''
            toast.success(
              `✅ ${imported} processo(s) importado(s)${skipped > 0 ? `, ${skipped} já existiam` : ''}\n` +
              `🔄 Monitoramento automático ativado! Alterações serão sincronizadas automaticamente.${convertedMsg}`,
              { duration: 8000 }
            )
          }
        } catch (linkError) {
          // Se falhar ao criar watch channel, ainda mostrar sucesso do upload
          console.error('Erro ao criar watch channel:', linkError)
          const errorDetail = linkError.response?.data?.detail
          const errorMsg = typeof errorDetail === 'object' && errorDetail?.message
            ? errorDetail.message.split('\n')[0]
            : 'Não foi possível ativar monitoramento automático'
          
          toast(
            `✅ ${imported} processo(s) importado(s)${skipped > 0 ? `, ${skipped} já existiam` : ''}\n` +
            `⚠️ ${errorMsg}`,
            { duration: 8000 }
          )
        }
      } else if (enableAutoSync && !data.can_monitor) {
        // Monitoramento ativado mas arquivo não pode ser monitorado
        toast(
          `✅ ${imported} processo(s) importado(s)${skipped > 0 ? `, ${skipped} já existiam` : ''}\n` +
          `ℹ️ Monitoramento automático não disponível para este tipo de arquivo.`,
          { duration: 6000 }
        )
      } else {
        if (imported > 0) {
          toast.success(`✅ ${imported} processo(s) importado(s)${skipped > 0 ? `, ${skipped} já existiam` : ''}`)
        } else if (skipped > 0) {
          toast.info(`ℹ️ ${skipped} processo(s) já existem no banco. Nenhum novo processo importado.`)
        } else {
          toast('Nenhum processo foi importado.', {
            icon: 'ℹ️',
            style: {
              background: '#3b82f6',
              color: '#fff',
            }
          })
        }
      }
      
      setGoogleDriveLink('')
      setPreviewData(null)
      setShowPreview(false)
    },
    onError: (error) => {
      console.error('Erro ao importar do Google Drive:', error)
      const errorDetail = error.response?.data?.detail
      
      // Se for um objeto com mensagem estruturada
      if (typeof errorDetail === 'object' && errorDetail.message) {
        // Mostrar mensagem completa (pode conter instruções de conversão)
        const fullMessage = errorDetail.message
        // Se a mensagem for muito longa, mostrar em múltiplas linhas ou truncar
        if (fullMessage.length > 200) {
          // Mostrar primeiras linhas importantes
          const lines = fullMessage.split('\n')
          const importantLines = lines.slice(0, 4).join('\n')
          toast.error(importantLines, { duration: 8000 })
        } else {
          toast.error(fullMessage, { duration: 6000 })
        }
      } else if (typeof errorDetail === 'string') {
        // Se for string direta
        toast.error(errorDetail, { duration: 6000 })
      } else {
        toast.error(error.message || 'Erro ao importar processos do Google Drive')
      }
    },
  })

  const handleDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile && (droppedFile.name.endsWith('.xlsx') || droppedFile.name.endsWith('.xls') || droppedFile.name.endsWith('.csv'))) {
      setFile(droppedFile)
      setPreviewData(null)
      setShowPreview(false)
    } else {
      toast.error('Por favor, selecione um arquivo Excel (.xlsx, .xls) ou CSV')
    }
  }

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
      setPreviewData(null)
      setShowPreview(false)
    }
  }

  const handlePreview = () => {
    if (file) {
      previewMutation.mutate(file)
    }
  }

  const handleFileUpload = () => {
    if (file) {
      uploadFileMutation.mutate(file)
    }
  }

  const handleGoogleDrivePreview = () => {
    if (!googleDriveLink.trim()) {
      toast.error('Por favor, insira um link do Google Drive')
      return
    }
    
    if (!googleDriveLink.includes('drive.google.com') && !googleDriveLink.includes('docs.google.com')) {
      toast.error('Por favor, insira um link válido do Google Drive ou Google Sheets')
      return
    }
    
    previewGoogleDriveMutation.mutate(googleDriveLink.trim())
  }

  const handleGoogleDriveUpload = () => {
    if (!googleDriveLink.trim()) {
      toast.error('Por favor, insira um link do Google Drive')
      return
    }
    
    if (!googleDriveLink.includes('drive.google.com') && !googleDriveLink.includes('docs.google.com')) {
      toast.error('Por favor, insira um link válido do Google Drive ou Google Sheets')
      return
    }
    
    uploadGoogleDriveMutation.mutate(googleDriveLink.trim())
  }

  const isLoading = previewMutation.isPending || uploadFileMutation.isPending || uploadGoogleDriveMutation.isPending || previewGoogleDriveMutation.isPending

  // Carregar email do Service Account quando mudar para modo Google Drive
  const loadServiceAccountEmail = async () => {
    if (serviceAccountEmail || loadingEmail) return
    
    setLoadingEmail(true)
    try {
      const response = await axios.get(`${API_URL}/api/sheets/service-account-email`)
      if (response.data?.service_account_email) {
        setServiceAccountEmail(response.data.service_account_email)
      }
    } catch (error) {
      console.error('Erro ao carregar email do Service Account:', error)
      // Não mostrar erro ao usuário, apenas não exibir o email
      // O email pode ser obtido manualmente se necessário
    } finally {
      setLoadingEmail(false)
    }
  }

  // Carregar email quando mudar para modo Google Drive
  useEffect(() => {
    if (uploadMode === 'google_drive' && !serviceAccountEmail && !loadingEmail) {
      loadServiceAccountEmail()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [uploadMode])

  return (
    <div className="h-full px-4 sm:px-6 lg:px-8 py-6 overflow-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Upload de Processos</h1>
        <p className="mt-2 text-gray-600">Importe processos em lote via planilha Excel ou CSV</p>
      </div>

      <div className="max-w-4xl mx-auto">
        {/* Tabs */}
        <div className="mb-6 border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => {
                setUploadMode('file')
                setPreviewData(null)
                setShowPreview(false)
              }}
              className={`${
                uploadMode === 'file'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
            >
              <FileUp className="h-5 w-5" />
              <span>Upload de Arquivo</span>
            </button>
            <button
              onClick={() => {
                setUploadMode('google_drive')
                setPreviewData(null)
                setShowPreview(false)
              }}
              className={`${
                uploadMode === 'google_drive'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
            >
              <LinkIcon className="h-5 w-5" />
              <span>Google Drive</span>
            </button>
          </nav>
        </div>

        {/* Modo: Upload de Arquivo */}
        {uploadMode === 'file' && (
          <>
            <div
              className={`border-2 border-dashed rounded-lg p-12 text-center ${
                dragging
                  ? 'border-blue-500 bg-blue-50'
                  : file
                  ? 'border-green-500 bg-green-50'
                  : 'border-gray-300 bg-white'
              }`}
              onDrop={handleDrop}
              onDragOver={(e) => {
                e.preventDefault()
                setDragging(true)
              }}
              onDragLeave={() => setDragging(false)}
            >
              {file ? (
                <div>
                  <FileSpreadsheet className="mx-auto h-12 w-12 text-green-500 mb-4" />
                  <p className="text-lg font-medium text-gray-900">{file.name}</p>
                  <p className="text-sm text-gray-500 mt-2">
                    {(file.size / 1024).toFixed(2)} KB
                  </p>
                </div>
              ) : (
                <div>
                  <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <p className="text-lg font-medium text-gray-900 mb-2">
                    Arraste e solte o arquivo Excel ou CSV aqui
                  </p>
                  <p className="text-sm text-gray-500 mb-4">ou</p>
                  <label className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 cursor-pointer">
                    Selecionar arquivo
                    <input
                      type="file"
                      className="hidden"
                      accept=".xlsx,.xls,.csv"
                      onChange={handleFileSelect}
                    />
                  </label>
                </div>
              )}
            </div>

            {file && (
              <div className="mt-6 flex justify-end space-x-3">
                <button
                  onClick={() => {
                    setFile(null)
                    setPreviewData(null)
                    setShowPreview(false)
                  }}
                  disabled={isLoading}
                  className="px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                >
                  Cancelar
                </button>
                <button
                  onClick={handlePreview}
                  disabled={isLoading}
                  className="px-4 py-2 border border-blue-300 text-sm font-medium rounded-md text-blue-700 bg-blue-50 hover:bg-blue-100 disabled:opacity-50 flex items-center space-x-2"
                >
                  <Eye className="h-4 w-4" />
                  <span>Preview</span>
                </button>
                <button
                  onClick={handleFileUpload}
                  disabled={isLoading || (previewData && !previewData.can_import)}
                  className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:bg-gray-400"
                >
                  {isLoading ? 'Enviando...' : 'Enviar'}
                </button>
              </div>
            )}

            {/* Preview */}
            {showPreview && previewData && (
              <div className="mt-6 bg-white border border-gray-300 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Preview e Validação</h3>
                  <button
                    onClick={() => setShowPreview(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>

                <div className="mb-4 grid grid-cols-4 gap-4">
                  <div className="bg-gray-50 p-3 rounded">
                    <div className="text-xs text-gray-600">Total de linhas</div>
                    <div className="text-lg font-bold text-gray-900">{previewData.total_rows}</div>
                  </div>
                  <div className="bg-green-50 p-3 rounded">
                    <div className="text-xs text-green-600">Válidas</div>
                    <div className="text-lg font-bold text-green-700">{previewData.summary.valid}</div>
                  </div>
                  <div className="bg-yellow-50 p-3 rounded">
                    <div className="text-xs text-yellow-600">Avisos</div>
                    <div className="text-lg font-bold text-yellow-700">{previewData.summary.warnings}</div>
                  </div>
                  <div className="bg-red-50 p-3 rounded">
                    <div className="text-xs text-red-600">Erros</div>
                    <div className="text-lg font-bold text-red-700">{previewData.summary.errors}</div>
                  </div>
                </div>

                {!previewData.can_import && (
                  <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
                    <div className="flex items-center space-x-2 text-red-800">
                      <AlertCircle className="h-5 w-5" />
                      <span className="font-medium">Importação bloqueada: {previewData.summary.errors} erro(s) crítico(s)</span>
                    </div>
                    <p className="text-sm text-red-700 mt-2">{previewData.message}</p>
                  </div>
                )}

                {previewData.can_import && (
                  <div className="mb-4 bg-green-50 border border-green-200 rounded-lg p-4">
                    <div className="flex items-center space-x-2 text-green-800">
                      <CheckCircle className="h-5 w-5" />
                      <span className="font-medium">Pronto para importar</span>
                    </div>
                    <p className="text-sm text-green-700 mt-2">{previewData.message}</p>
                  </div>
                )}

                {/* Preview das linhas */}
                <div className="mt-4 max-h-96 overflow-y-auto">
                  <table className="min-w-full divide-y divide-gray-200 text-xs">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-700">Linha</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-700">Status</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-700">PROCESSO ADM 1DOC</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-700">PROCESSO JUDICIAL</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-700">Erros/Avisos</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {previewData.preview.map((row, idx) => (
                        <tr key={idx} className={row.status === 'error' ? 'bg-red-50' : row.status === 'warning' ? 'bg-yellow-50' : ''}>
                          <td className="px-3 py-2 text-gray-900">{row.row_number}</td>
                          <td className="px-3 py-2">
                            {row.status === 'error' && <span className="text-red-600 font-medium">Erro</span>}
                            {row.status === 'warning' && <span className="text-yellow-600 font-medium">Aviso</span>}
                            {row.status === 'valid' && <span className="text-green-600 font-medium">OK</span>}
                          </td>
                          <td className="px-3 py-2 text-gray-900">{row.data.processo_adm_1doc || '—'}</td>
                          <td className="px-3 py-2 text-gray-900">{row.data.processo_judicial || '—'}</td>
                          <td className="px-3 py-2">
                            <div className="space-y-1">
                              {row.errors.map((err, i) => (
                                <div key={i} className="text-red-600 text-xs">{err.message}</div>
                              ))}
                              {row.warnings.map((warn, i) => (
                                <div key={i} className="text-yellow-600 text-xs">{warn.message}</div>
                              ))}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}

        {/* Modo: Google Drive */}
        {uploadMode === 'google_drive' && (
          <>
            <div className="bg-white border-2 border-gray-300 rounded-lg p-8">
              <div className="text-center mb-6">
                <LinkIcon className="mx-auto h-12 w-12 text-blue-500 mb-4" />
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  Importar do Google Drive
                </h2>
                <p className="text-sm text-gray-600">
                  Cole o link do arquivo ou planilha do Google Drive
                </p>
              </div>

              <div className="space-y-4">
                {/* Email do Service Account */}
                {serviceAccountEmail && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-start space-x-2">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-blue-900 mb-1">
                          Email do Service Account (compartilhe a planilha com este email):
                        </p>
                        <div className="flex items-center space-x-2">
                          <code className="text-sm font-mono bg-white px-3 py-2 rounded border border-blue-300 text-blue-800 flex-1">
                            {serviceAccountEmail}
                          </code>
                          <button
                            onClick={() => {
                              navigator.clipboard.writeText(serviceAccountEmail)
                              toast.success('Email copiado!')
                            }}
                            className="px-3 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                            title="Copiar email"
                          >
                            Copiar
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                <div>
                  <label htmlFor="google-drive-link" className="block text-sm font-medium text-gray-700 mb-2">
                    Link do Google Drive ou Google Sheets
                  </label>
                  <input
                    id="google-drive-link"
                    type="url"
                    value={googleDriveLink}
                    onChange={(e) => setGoogleDriveLink(e.target.value)}
                    placeholder="https://docs.google.com/spreadsheets/d/..."
                    className="block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm"
                    disabled={isLoading}
                  />
                </div>

                {/* Checkbox de Monitoramento Automático */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <label className="flex items-start space-x-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={enableAutoSync}
                      onChange={(e) => setEnableAutoSync(e.target.checked)}
                      className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      disabled={isLoading}
                    />
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-green-900">
                          🔄 Monitoramento Automático
                        </span>
                      </div>
                      <p className="text-xs text-green-700 mt-1">
                        Quando ativado, o sistema monitora automaticamente alterações na planilha e sincroniza os dados sem necessidade de upload manual. 
                        Funciona apenas com Google Sheets nativos (arquivos Excel/CSV serão convertidos automaticamente).
                      </p>
                    </div>
                  </label>
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    onClick={() => {
                      setGoogleDriveLink('')
                      setPreviewData(null)
                      setShowPreview(false)
                    }}
                    disabled={isLoading}
                    className="px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                  >
                    Limpar
                  </button>
                  <button
                    onClick={handleGoogleDrivePreview}
                    disabled={isLoading || !googleDriveLink.trim()}
                    className="px-4 py-2 border border-blue-300 text-sm font-medium rounded-md text-blue-700 bg-blue-50 hover:bg-blue-100 disabled:opacity-50 flex items-center space-x-2"
                  >
                    <Eye className="h-4 w-4" />
                    <span>Preview</span>
                  </button>
                  <button
                    onClick={handleGoogleDriveUpload}
                    disabled={isLoading || !googleDriveLink.trim() || (previewData && !previewData.can_import)}
                    className="px-6 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:bg-gray-400 disabled:cursor-not-allowed"
                  >
                    {isLoading ? 'Importando...' : 'Importar'}
                  </button>
                </div>
              </div>
            </div>

            {/* Preview para Google Drive */}
            {showPreview && previewData && uploadMode === 'google_drive' && (
              <div className="mt-6 bg-white border border-gray-300 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Preview e Validação</h3>
                  <button
                    onClick={() => setShowPreview(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>

                <div className="mb-4 grid grid-cols-4 gap-4">
                  <div className="bg-gray-50 p-3 rounded">
                    <div className="text-xs text-gray-600">Total de linhas</div>
                    <div className="text-lg font-bold text-gray-900">{previewData.total_rows}</div>
                  </div>
                  <div className="bg-green-50 p-3 rounded">
                    <div className="text-xs text-green-600">Válidas</div>
                    <div className="text-lg font-bold text-green-700">{previewData.summary.valid}</div>
                  </div>
                  <div className="bg-yellow-50 p-3 rounded">
                    <div className="text-xs text-yellow-600">Avisos</div>
                    <div className="text-lg font-bold text-yellow-700">{previewData.summary.warnings}</div>
                  </div>
                  <div className="bg-red-50 p-3 rounded">
                    <div className="text-xs text-red-600">Erros</div>
                    <div className="text-lg font-bold text-red-700">{previewData.summary.errors}</div>
                  </div>
                </div>

                {!previewData.can_import && (
                  <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
                    <div className="flex items-center space-x-2 text-red-800">
                      <AlertCircle className="h-5 w-5" />
                      <span className="font-medium">Importação bloqueada: {previewData.summary.errors} erro(s) crítico(s)</span>
                    </div>
                    <p className="text-sm text-red-700 mt-2">{previewData.message}</p>
                  </div>
                )}

                {previewData.can_import && (
                  <div className="mb-4 bg-green-50 border border-green-200 rounded-lg p-4">
                    <div className="flex items-center space-x-2 text-green-800">
                      <CheckCircle className="h-5 w-5" />
                      <span className="font-medium">Pronto para importar</span>
                    </div>
                    <p className="text-sm text-green-700 mt-2">{previewData.message}</p>
                  </div>
                )}

                {/* Preview das linhas */}
                <div className="mt-4 max-h-96 overflow-y-auto">
                  <table className="min-w-full divide-y divide-gray-200 text-xs">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-700">Linha</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-700">Status</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-700">PROCESSO ADM 1DOC</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-700">PROCESSO JUDICIAL</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-700">Erros/Avisos</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {previewData.preview.map((row, idx) => (
                        <tr key={idx} className={row.status === 'error' ? 'bg-red-50' : row.status === 'warning' ? 'bg-yellow-50' : ''}>
                          <td className="px-3 py-2 text-gray-900">{row.row_number}</td>
                          <td className="px-3 py-2">
                            {row.status === 'error' && <span className="text-red-600 font-medium">Erro</span>}
                            {row.status === 'warning' && <span className="text-yellow-600 font-medium">Aviso</span>}
                            {row.status === 'valid' && <span className="text-green-600 font-medium">OK</span>}
                          </td>
                          <td className="px-3 py-2 text-gray-900">{row.data.processo_adm_1doc || '—'}</td>
                          <td className="px-3 py-2 text-gray-900">{row.data.processo_judicial || '—'}</td>
                          <td className="px-3 py-2">
                            <div className="space-y-1">
                              {row.errors.map((err, i) => (
                                <div key={i} className="text-red-600 text-xs">{err.message}</div>
                              ))}
                              {row.warnings.map((warn, i) => (
                                <div key={i} className="text-yellow-600 text-xs">{warn.message}</div>
                              ))}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="text-sm font-medium text-blue-900 mb-2">Como compartilhar no Google Drive:</h3>
              <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
                <li>Abra o arquivo no Google Drive ou Google Sheets</li>
                <li>Clique em "Compartilhar" (botão no canto superior direito)</li>
                {serviceAccountEmail ? (
                  <li>Adicione o email: <strong className="font-mono bg-white px-2 py-1 rounded">{serviceAccountEmail}</strong></li>
                ) : (
                  <li>Adicione o email do Service Account (veja acima ou acesse <code className="bg-white px-1 rounded">/api/sheets/service-account-email</code>)</li>
                )}
                <li>Defina permissão como "Visualizador"</li>
                <li>Copie o link e cole acima</li>
              </ol>
            </div>
          </>
        )}

        {/* Informações sobre formato */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-blue-900 mb-2">Formato da planilha</h3>
          <div className="text-sm text-blue-800 space-y-1">
            <p><strong>Colunas obrigatórias:</strong> PROCESSO ADM 1DOC ou PROCESSO JUDICIAL</p>
            <p><strong>Colunas opcionais:</strong> PARTES, DATA RECEBIMENTO (MÊS/ANO), TEMA – OBSERVAÇÕES, PRAZO INFO – ESTAG (DIA/MÊS), PRAZO FINAL (DD/MM), TIPO DE ATO, DATA DE REALIZAÇÃO DO ATO (DD/MM/YYYY)</p>
            <p><strong>Formatos suportados:</strong> XLSX, XLS, CSV</p>
            <p><strong>Ordem das colunas:</strong> Não importa - o sistema identifica por nome</p>
          </div>
        </div>
      </div>
    </div>
  )
}
