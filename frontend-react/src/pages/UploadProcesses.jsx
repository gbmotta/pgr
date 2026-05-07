import { useState, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import axios from 'axios'
import { Upload, FileSpreadsheet, Link as LinkIcon, FileUp, FileDown, Grid3x3, Eye, AlertCircle, CheckCircle, X, Plus, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { API_URL } from '@/lib/apiConfig'
import { cn } from '@/lib/utils'

/** Mensagem legível a partir de error.response.data.detail (FastAPI). */
function formatApiDetail(detail) {
  if (detail == null || detail === '') return null
  if (typeof detail === 'string') return detail
  if (typeof detail === 'object' && typeof detail.message === 'string') return detail.message
  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0]
    if (typeof first === 'string') return first
    if (first?.msg) return first.msg
  }
  return null
}

const GRID_COLUMNS = [
  { key: 'processo_adm_1doc', title: 'PROCESSO ADM 1DOC' },
  { key: 'processo_judicial', title: 'PROCESSO JUDICIAL' },
  { key: 'partes', title: 'PARTES' },
  { key: 'data_recebimento_mes_ano', title: 'DATA RECEBIMENTO (MÊS/ANO)' },
  { key: 'tema_observacoes', title: 'TEMA – OBSERVAÇÕES' },
  { key: 'prazo_info_estag', title: 'PRAZO INFO – ESTAG (DIA/MÊS)' },
  { key: 'prazo_final', title: 'PRAZO FINAL (DD/MM)' },
  { key: 'tipo_ato', title: 'TIPO DE ATO' },
  { key: 'data_realizacao_ato', title: 'DATA REALIZAÇÃO ATO (DD/MM/YYYY)' },
]

function createEmptyGridRow() {
  return {
    processo_adm_1doc: '',
    processo_judicial: '',
    partes: '',
    data_recebimento_mes_ano: '',
    tema_observacoes: '',
    prazo_info_estag: '',
    prazo_final: '',
    tipo_ato: '',
    data_realizacao_ato: '',
  }
}

export default function UploadProcesses() {
  const [file, setFile] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [googleDriveLink, setGoogleDriveLink] = useState('')
  const [uploadMode, setUploadMode] = useState('grid')
  const [previewData, setPreviewData] = useState(null)
  const [showPreview, setShowPreview] = useState(false)
  const [serviceAccountEmail, setServiceAccountEmail] = useState(null)
  const [privacyNote, setPrivacyNote] = useState(null)
  const [loadingEmail, setLoadingEmail] = useState(false)
  const [enableAutoSync, setEnableAutoSync] = useState(true) // Monitoramento automático ativado por padrão
  const [gridRows, setGridRows] = useState(() =>
    Array.from({ length: 12 }, () => createEmptyGridRow())
  )

  const gridImportMutation = useMutation({
    mutationFn: async (rows) => {
      const response = await axios.post(`${API_URL}/api/processes/import-grid`, { rows })
      return response.data
    },
    onSuccess: (data) => {
      const imported = data.imported ?? 0
      const skipped = data.skipped ?? 0
      if (imported > 0) {
        toast.success(
          data.message ||
            `✅ ${imported} processo(s) importado(s)${skipped > 0 ? `, ${skipped} já existiam` : ''}`
        )
      } else if (skipped > 0) {
        toast.info(`ℹ️ ${skipped} linha(s) já tinham processo na sua conta. Nada de novo importado.`)
      } else {
        toast.error('Nenhum processo importado.')
      }
    },
    onError: (error) => {
      toast.error(formatApiDetail(error.response?.data?.detail) || 'Erro ao importar da planilha')
    },
  })

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
          const errorMsg =
            formatApiDetail(errorDetail) || 'Não foi possível ativar monitoramento automático'
          
          toast(
            `✅ ${imported} processo(s) importado(s)${skipped > 0 ? `, ${skipped} já existiam` : ''}\n` +
            `⚠️ ${errorMsg}`,
            { duration: 12000 }
          )
        }
      } else if (enableAutoSync && !data.can_monitor) {
        // Monitoramento pedido mas backend não ativou (conversão falhou, cota, ou tipo sem Sheets nativo)
        const syncHint = data.conversion_warning
          ? ' Não foi possível criar/usar Google Sheets nativo para webhook (ex.: cota do Drive da service account). Libere espaço na conta da service account ou crie uma planilha nativa (Arquivo → Novo → Planilha), copie os dados e compartilhe o novo link.'
          : ' É necessário Google Sheets nativo no Drive ou conversão automática bem-sucedida (Excel/CSV no Drive são convertidos na conta da service account).'
        toast(
          `✅ ${imported} processo(s) importado(s)${skipped > 0 ? `, ${skipped} já existiam` : ''}\n` +
          `ℹ️ Monitoramento automático indisponível.${syncHint}`,
          { duration: 10000 }
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

  const isLoading =
    previewMutation.isPending ||
    uploadFileMutation.isPending ||
    uploadGoogleDriveMutation.isPending ||
    previewGoogleDriveMutation.isPending ||
    gridImportMutation.isPending

  const gridReady = gridRows.some(
    (r) => (r.processo_adm_1doc || '').trim() || (r.processo_judicial || '').trim()
  )
  const fileOrLinkReady =
    uploadMode === 'file'
      ? !!file
      : uploadMode === 'google_drive'
        ? googleDriveLink.trim().length > 0
        : gridReady
  const importFlowStep = uploadMode === 'grid' ? (gridReady ? 3 : 2) : fileOrLinkReady ? 3 : 2

  const updateGridCell = (rowIndex, key, value) => {
    setGridRows((prev) => {
      const next = [...prev]
      next[rowIndex] = { ...next[rowIndex], [key]: value }
      return next
    })
  }

  const addGridRow = () => {
    setGridRows((prev) => [...prev, createEmptyGridRow()])
  }

  const removeGridRow = (rowIndex) => {
    setGridRows((prev) => (prev.length <= 1 ? prev : prev.filter((_, i) => i !== rowIndex)))
  }

  const clearGrid = () => {
    setGridRows(Array.from({ length: 12 }, () => createEmptyGridRow()))
  }

  const handleGridImport = () => {
    const hasIdentifier = gridRows.some(
      (r) => (r.processo_adm_1doc || '').trim() || (r.processo_judicial || '').trim()
    )
    if (!hasIdentifier) {
      toast.error('Preencha PROCESSO ADM 1DOC ou PROCESSO JUDICIAL em pelo menos uma linha.')
      return
    }
    gridImportMutation.mutate(gridRows)
  }

  const downloadSpreadsheetTemplate = async (format, withExample = false) => {
    try {
      const response = await axios.get(`${API_URL}/api/processes/spreadsheet-template`, {
        params: { format, example: withExample },
        responseType: 'blob',
      })
      const name =
        format === 'csv' ? 'PGR_modelo_processos.csv' : 'PGR_modelo_processos.xlsx'
      const mime =
        format === 'csv'
          ? 'text/csv;charset=utf-8'
          : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      const url = window.URL.createObjectURL(new Blob([response.data], { type: mime }))
      const a = document.createElement('a')
      a.href = url
      a.download = name
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
      toast.success('Modelo descarregado. Preencha e envie abaixo.')
    } catch (e) {
      console.error(e)
      toast.error(e.response?.data?.detail || 'Erro ao descarregar modelo')
    }
  }

  // Carregar email do Service Account quando mudar para modo Google Drive
  const loadServiceAccountEmail = async () => {
    if (serviceAccountEmail || loadingEmail) return
    
    setLoadingEmail(true)
    try {
      const response = await axios.get(`${API_URL}/api/sheets/service-account-email`)
      if (response.data?.service_account_email) {
        setServiceAccountEmail(response.data.service_account_email)
      }
      setPrivacyNote(response.data?.privacy_note || null)
    } catch (error) {
      console.error('Erro ao carregar email do Service Account:', error)
      // Não mostrar erro ao usuário, apenas não exibir o email
      // O email pode ser obtido manualmente se necessário
    } finally {
      setLoadingEmail(false)
    }
  }

  // Preferência de separador (definida em Configurações)
  useEffect(() => {
    try {
      const pref = localStorage.getItem('pgr_import_mode_preference')
      if (pref === 'grid' || pref === 'file' || pref === 'google_drive') {
        setUploadMode(pref)
      }
    } catch {
      /* ignore */
    }
  }, [])

  // Carregar email quando mudar para modo Google Drive
  useEffect(() => {
    if (uploadMode === 'google_drive' && !serviceAccountEmail && !loadingEmail) {
      loadServiceAccountEmail()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [uploadMode])

  return (
    <div className="h-full overflow-auto py-6">
      <section className="surface-panel mb-8 px-6 py-6 lg:px-8">
        <span className="hero-badge">
          <Upload className="h-3.5 w-3.5" />
          Entrada de dados
        </span>
        <h1 className="page-title mt-4">Importar dados</h1>
        <p className="page-subtitle mt-3">
          Preencha a planilha aqui no PGR, envie um ficheiro ou ligue o Google Sheets — os processos ficam
          sempre associados à sua conta.
        </p>
        <div className="mt-5 max-w-3xl rounded-2xl border border-[#d8e0e7] bg-[#f8fbfd] px-4 py-3 text-sm text-slate-700">
          <p className="font-medium text-slate-800">Privacidade e dados</p>
          <p className="mt-1">
            Cada conta PGR vê apenas os seus processos. No modo ficheiro, a planilha não sai do seu
            computador até ao envio; os dados importados ficam na base do PGR. No modo Google, a
            planilha permanece no Google Drive; a service account só acede ao que partilhar como leitor.
          </p>
        </div>
      </section>

      <div className={`mx-auto ${uploadMode === 'grid' ? 'max-w-[90rem]' : 'max-w-4xl'}`}>
        <div className="surface-panel mb-6 p-3">
          <nav className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => {
                setUploadMode('grid')
                setPreviewData(null)
                setShowPreview(false)
              }}
              className={`${
                uploadMode === 'grid'
                  ? 'pill-button pill-button-active'
                  : 'pill-button pill-button-idle'
              } whitespace-nowrap`}
            >
              <Grid3x3 className="h-5 w-5" />
              <span>Planilha no PGR</span>
            </button>
            <button
              type="button"
              onClick={() => {
                setUploadMode('file')
                setPreviewData(null)
                setShowPreview(false)
              }}
              className={`${
                uploadMode === 'file'
                  ? 'pill-button pill-button-active'
                  : 'pill-button pill-button-idle'
              } whitespace-nowrap`}
            >
              <FileUp className="h-5 w-5" />
              <span>Só ficheiro (sem Google)</span>
            </button>
            <button
              type="button"
              onClick={() => {
                setUploadMode('google_drive')
                setPreviewData(null)
                setShowPreview(false)
              }}
              className={`${
                uploadMode === 'google_drive'
                  ? 'pill-button pill-button-active'
                  : 'pill-button pill-button-idle'
              } whitespace-nowrap`}
            >
              <LinkIcon className="h-5 w-5" />
              <span>Google Sheets + partilha</span>
            </button>
          </nav>
        </div>

        <ol
          className="mb-6 flex flex-wrap items-center gap-3 rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 shadow-sm"
          aria-label="Passos da importação"
        >
          <li
            className="flex items-center gap-2 font-medium text-emerald-700"
            aria-label="Passo 1: modo de importação (separadores acima)"
          >
            <span
              className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-emerald-600 text-xs font-bold text-white"
              aria-hidden
            >
              ✓
            </span>
            Separador escolhido
          </li>
          <span className="hidden text-slate-300 sm:inline" aria-hidden>
            →
          </span>
          <li
            className={cn(
              'flex items-center gap-2',
              importFlowStep === 2 ? 'font-semibold text-blue-800' : 'text-slate-500'
            )}
            aria-current={importFlowStep === 2 ? 'step' : undefined}
          >
            <span
              className={cn(
                'flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-bold',
                importFlowStep === 2
                  ? 'bg-blue-600 text-white ring-2 ring-blue-200 ring-offset-2'
                  : 'bg-slate-200 text-slate-600'
              )}
              aria-hidden
            >
              2
            </span>
            {uploadMode === 'grid'
              ? 'Preencher a grelha'
              : uploadMode === 'file'
                ? 'Selecionar ficheiro e pré-visualizar'
                : 'Colar link e pré-visualizar'}
          </li>
          <span className="hidden text-slate-300 sm:inline" aria-hidden>
            →
          </span>
          <li
            className={cn(
              'flex items-center gap-2',
              importFlowStep === 3 ? 'font-semibold text-blue-800' : 'text-slate-500'
            )}
            aria-current={importFlowStep === 3 ? 'step' : undefined}
          >
            <span
              className={cn(
                'flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-bold',
                importFlowStep === 3
                  ? 'bg-blue-600 text-white ring-2 ring-blue-200 ring-offset-2'
                  : 'bg-slate-200 text-slate-600'
              )}
              aria-hidden
            >
              3
            </span>
            Importar para o PGR
          </li>
        </ol>

        {/* Modo: planilha editável no browser */}
        {uploadMode === 'grid' && (
          <div className="space-y-4">
            <div className="rounded-lg border border-emerald-200 bg-emerald-50/90 px-4 py-3 text-sm text-emerald-950">
              <p className="font-medium">Preencha as linhas como numa folha de cálculo</p>
              <p className="mt-1 text-xs text-emerald-900/90">
                Cada linha com <strong>PROCESSO ADM 1DOC</strong> ou <strong>PROCESSO JUDICIAL</strong> vira um
                processo na sua conta. Pode usar as colunas opcionais (PARTES, prazos, etc.) como no modelo
                descarregável — a ordem das colunas não importa. Linhas vazias são ignoradas.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <button
                type="button"
                onClick={addGridRow}
                disabled={isLoading}
                className="inline-flex items-center gap-1.5 rounded-md bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
              >
                <Plus className="h-4 w-4" />
                Adicionar linha
              </button>
              <button
                type="button"
                onClick={clearGrid}
                disabled={isLoading}
                className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
              >
                Limpar tudo
              </button>
              <button
                type="button"
                onClick={handleGridImport}
                disabled={isLoading}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
              >
                {gridImportMutation.isPending ? 'A importar…' : 'Importar processos para o PGR'}
              </button>
            </div>

            <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
              <table className="min-w-full border-collapse text-left text-xs">
                <thead>
                  <tr className="border-b border-gray-200 bg-slate-100">
                    <th className="sticky left-0 z-10 w-10 border-r border-gray-200 bg-slate-100 px-2 py-2 text-center font-semibold text-slate-600">
                      #
                    </th>
                    {GRID_COLUMNS.map((col) => (
                      <th
                        key={col.key}
                        className="min-w-[10rem] max-w-[14rem] whitespace-normal px-2 py-2 font-semibold text-slate-800"
                        title={col.title}
                      >
                        {col.title}
                        {(col.key === 'processo_adm_1doc' || col.key === 'processo_judicial') && (
                          <span className="ml-0.5 text-red-600">*</span>
                        )}
                      </th>
                    ))}
                    <th className="w-12 px-1 py-2 text-center font-semibold text-slate-600"> </th>
                  </tr>
                </thead>
                <tbody>
                  {gridRows.map((row, rowIndex) => (
                    <tr key={rowIndex} className="group border-b border-gray-100 hover:bg-slate-50/80">
                      <td className="sticky left-0 z-10 border-r border-gray-100 bg-white px-2 py-1 text-center text-slate-500 tabular-nums group-hover:bg-slate-50/80">
                        {rowIndex + 1}
                      </td>
                      {GRID_COLUMNS.map((col) => (
                        <td key={col.key} className="p-0 align-top">
                          <input
                            type="text"
                            value={row[col.key] ?? ''}
                            onChange={(e) => updateGridCell(rowIndex, col.key, e.target.value)}
                            className="box-border w-full min-w-[8rem] border-0 bg-transparent px-2 py-1.5 text-xs text-gray-900 outline-none ring-inset focus:ring-2 focus:ring-blue-400/60"
                            placeholder="—"
                            disabled={isLoading}
                            autoComplete="off"
                          />
                        </td>
                      ))}
                      <td className="px-1 py-1 text-center align-middle">
                        <button
                          type="button"
                          onClick={() => removeGridRow(rowIndex)}
                          disabled={isLoading || gridRows.length <= 1}
                          className="rounded p-1 text-gray-400 hover:bg-red-50 hover:text-red-600 disabled:opacity-30"
                          title="Remover linha"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Modo: Upload de Arquivo */}
        {uploadMode === 'file' && (
          <>
            <div className="mb-6 rounded-lg border border-indigo-200 bg-indigo-50/80 px-4 py-4">
              <div className="flex items-start gap-3">
                <FileDown className="h-8 w-8 text-indigo-600 shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-semibold text-indigo-950">
                    Criar planilha a partir do modelo do PGR
                  </h3>
                  <p className="mt-1 text-xs text-indigo-900/90">
                    Gere um Excel ou CSV já com os cabeçalhos corretos. Preencha as linhas no seu
                    computador (ou copie para o Google Sheets) e use a área de envio abaixo.
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() => downloadSpreadsheetTemplate('xlsx', false)}
                      disabled={isLoading}
                      className="inline-flex items-center gap-1.5 rounded-md bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
                    >
                      <FileSpreadsheet className="h-3.5 w-3.5" />
                      Modelo vazio (.xlsx)
                    </button>
                    <button
                      type="button"
                      onClick={() => downloadSpreadsheetTemplate('csv', false)}
                      disabled={isLoading}
                      className="inline-flex items-center gap-1.5 rounded-md border border-indigo-300 bg-white px-3 py-1.5 text-xs font-medium text-indigo-800 hover:bg-indigo-50 disabled:opacity-50"
                    >
                      Modelo vazio (.csv)
                    </button>
                    <button
                      type="button"
                      onClick={() => downloadSpreadsheetTemplate('xlsx', true)}
                      disabled={isLoading}
                      className="inline-flex items-center gap-1.5 rounded-md border border-indigo-300 bg-white px-3 py-1.5 text-xs font-medium text-indigo-800 hover:bg-indigo-50 disabled:opacity-50"
                    >
                      Excel com linha de exemplo
                    </button>
                  </div>
                </div>
              </div>
            </div>

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
                  Onboarding: (1) conta no PGR → (2) copiar email da service account abaixo → (3) partilhar a
                  planilha no Google como <strong>Leitor</strong> com esse email → importar ou vincular o link.
                </p>
              </div>

              <div className="space-y-4">
                {privacyNote && (
                  <p className="text-xs text-slate-600 bg-slate-50 border border-slate-200 rounded-md p-3">
                    {privacyNote}
                  </p>
                )}
                <p className="text-xs text-slate-600">
                  Quer montar a lista no Excel? Na aba <strong>Só ficheiro (sem Google)</strong> pode
                  descarregar o modelo, ou use <strong>Planilha no PGR</strong> para preencher no browser.
                  Depois pode copiar para o Google Sheets e partilhar o link aqui.
                </p>
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
          <div className="text-sm text-blue-800 space-y-3">
            <div>
              <p className="font-medium text-blue-900">Colunas obrigatórias</p>
              <p className="mt-0.5">
                Pelo menos uma: <strong>PROCESSO ADM 1DOC</strong> ou <strong>PROCESSO JUDICIAL</strong> (o
                sistema usa o nome exato do cabeçalho).
              </p>
            </div>
            <div>
              <p className="font-medium text-blue-900">Colunas opcionais</p>
              <ul className="mt-1 list-disc list-inside space-y-0.5">
                <li>PARTES</li>
                <li>DATA RECEBIMENTO (MÊS/ANO)</li>
                <li>TEMA – OBSERVAÇÕES</li>
                <li>PRAZO INFO – ESTAG (DIA/MÊS)</li>
                <li>PRAZO FINAL (DD/MM)</li>
                <li>TIPO DE ATO</li>
                <li>DATA DE REALIZAÇÃO DO ATO (DD/MM/YYYY)</li>
              </ul>
            </div>
            <p>
              <strong>Formatos suportados:</strong> XLSX, XLS, CSV
            </p>
            <p>
              <strong>Ordem das colunas:</strong> não importa — o sistema identifica pelo nome do cabeçalho.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
