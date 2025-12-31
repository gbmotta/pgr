import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import axios from 'axios'
import { Upload, FileSpreadsheet } from 'lucide-react'
import toast from 'react-hot-toast'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function UploadProcesses() {
  const [file, setFile] = useState(null)
  const [dragging, setDragging] = useState(false)

  const uploadMutation = useMutation({
    mutationFn: async (file) => {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await axios.post(`${API_URL}/processes/upload-excel`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return response.data
    },
    onSuccess: (data) => {
      toast.success(`Processos importados: ${data.imported || 0}`)
      setFile(null)
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Erro ao importar processos')
    },
  })

  const handleDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile && (droppedFile.name.endsWith('.xlsx') || droppedFile.name.endsWith('.xls'))) {
      setFile(droppedFile)
    } else {
      toast.error('Por favor, selecione um arquivo Excel (.xlsx ou .xls)')
    }
  }

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
    }
  }

  const handleUpload = () => {
    if (file) {
      uploadMutation.mutate(file)
    }
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Upload de Processos</h1>
        <p className="mt-2 text-gray-600">Importe processos em lote via planilha Excel</p>
      </div>

      <div className="max-w-3xl mx-auto">
        <div
          className={`border-2 border-dashed rounded-lg p-12 text-center ${
            dragging
              ? 'border-primary-500 bg-primary-50'
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
                Arraste e solte o arquivo Excel aqui
              </p>
              <p className="text-sm text-gray-500 mb-4">ou</p>
              <label className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 cursor-pointer">
                Selecionar arquivo
                <input
                  type="file"
                  className="hidden"
                  accept=".xlsx,.xls"
                  onChange={handleFileSelect}
                />
              </label>
            </div>
          )}
        </div>

        {file && (
          <div className="mt-6 flex justify-end">
            <button
              onClick={() => setFile(null)}
              className="mr-3 px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              onClick={handleUpload}
              disabled={uploadMutation.isPending}
              className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50"
            >
              {uploadMutation.isPending ? 'Enviando...' : 'Enviar'}
            </button>
          </div>
        )}

        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-blue-900 mb-2">Formato da planilha</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Colunas obrigatórias: Protocolo, Tipo, Requerente</li>
            <li>• Tipos válidos: PROM_CAP, PROG_MER</li>
            <li>• O sistema gera automaticamente checklist e prazos</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

