import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { Checkbox } from '@/components/ui/checkbox'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { CheckCircle2, Circle, FileText } from 'lucide-react'
import toast from 'react-hot-toast'
import { cn } from '@/lib/utils'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'

/**
 * Componente de Checklist de Documentos Jurídicos
 * 
 * Exibe uma lista de documentos com checkboxes que podem ser marcados/desmarcados.
 * Salva o estado automaticamente no backend quando um item é alterado.
 */
export default function DocumentChecklist({ 
  processProtocol,
  documents = [],
  onUpdate 
}) {
  const queryClient = useQueryClient()
  const [updating, setUpdating] = useState(new Set())

  // Mutation para atualizar o checklist
  const updateMutation = useMutation({
    mutationFn: async ({ documentCode, provided }) => {
      const response = await axios.put(
        `${API_URL}/api/processes/${processProtocol}/documents/${documentCode}`,
        null,
        {
          params: { provided }
        }
      )
      return response.data
    },
    onSuccess: (data, variables) => {
      toast.success(`${data.document.name} ${variables.provided ? 'marcado' : 'desmarcado'}`)
      // Invalidar cache do processo para atualizar a lista
      queryClient.invalidateQueries(['process', processProtocol])
      if (onUpdate) {
        onUpdate(data.document)
      }
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Erro ao atualizar checklist')
    },
    onSettled: (data, error, variables) => {
      // Remover do conjunto de atualização
      setUpdating(prev => {
        const next = new Set(prev)
        next.delete(variables.documentCode)
        return next
      })
    }
  })

  const handleToggle = (documentCode, currentProvided) => {
    const newProvided = !currentProvided
    
    // Adicionar ao conjunto de atualização
    setUpdating(prev => new Set(prev).add(documentCode))
    
    // Atualizar no backend
    updateMutation.mutate({
      documentCode,
      provided: newProvided
    })
  }

  // Se não houver documentos, exibir mensagem
  if (!documents || documents.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500 font-sans">Nenhum documento no checklist</p>
        </CardContent>
      </Card>
    )
  }

  // Separar documentos obrigatórios e opcionais
  const requiredDocs = documents.filter(doc => doc.required)
  const optionalDocs = documents.filter(doc => !doc.required)

  return (
    <Card className="border-[#1A2B3C]/20">
      <CardHeader className="bg-[#1A2B3C] text-white">
        <CardTitle className="text-xl font-serif font-bold">
          Checklist de Documentos
        </CardTitle>
      </CardHeader>
      <CardContent className="p-6">
        <div className="space-y-6">
          {/* Documentos Obrigatórios */}
          {requiredDocs.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-4 font-sans uppercase tracking-wide">
                Documentos Obrigatórios
              </h3>
              <div className="space-y-3">
                {requiredDocs.map((doc) => {
                  const isUpdating = updating.has(doc.code)
                  const isChecked = doc.provided || false
                  
                  return (
                    <div
                      key={doc.code}
                      className={cn(
                        "flex items-center space-x-3 p-3 rounded-lg border transition-colors",
                        isChecked
                          ? "bg-green-50 border-green-200"
                          : "bg-white border-gray-200 hover:border-gray-300",
                        isUpdating && "opacity-50"
                      )}
                    >
                      <Checkbox
                        id={`doc-${doc.code}`}
                        checked={isChecked}
                        onCheckedChange={() => handleToggle(doc.code, isChecked)}
                        disabled={isUpdating}
                        className="border-[#1A2B3C] data-[state=checked]:bg-[#1A2B3C]"
                      />
                      <label
                        htmlFor={`doc-${doc.code}`}
                        className={cn(
                          "flex-1 cursor-pointer font-sans",
                          isChecked ? "text-gray-900 font-medium" : "text-gray-700"
                        )}
                      >
                        <div className="flex items-center justify-between">
                          <span>{doc.name}</span>
                          {isChecked && (
                            <CheckCircle2 className="h-5 w-5 text-green-600" />
                          )}
                        </div>
                        {doc.provided_date && (
                          <p className="text-xs text-gray-500 mt-1">
                            Fornecido em: {new Date(doc.provided_date).toLocaleDateString('pt-BR')}
                          </p>
                        )}
                      </label>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Documentos Opcionais */}
          {optionalDocs.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-4 font-sans uppercase tracking-wide">
                Documentos Opcionais
              </h3>
              <div className="space-y-3">
                {optionalDocs.map((doc) => {
                  const isUpdating = updating.has(doc.code)
                  const isChecked = doc.provided || false
                  
                  return (
                    <div
                      key={doc.code}
                      className={cn(
                        "flex items-center space-x-3 p-3 rounded-lg border transition-colors",
                        isChecked
                          ? "bg-blue-50 border-blue-200"
                          : "bg-white border-gray-200 hover:border-gray-300",
                        isUpdating && "opacity-50"
                      )}
                    >
                      <Checkbox
                        id={`doc-${doc.code}`}
                        checked={isChecked}
                        onCheckedChange={() => handleToggle(doc.code, isChecked)}
                        disabled={isUpdating}
                        className="border-[#1A2B3C] data-[state=checked]:bg-[#1A2B3C]"
                      />
                      <label
                        htmlFor={`doc-${doc.code}`}
                        className={cn(
                          "flex-1 cursor-pointer font-sans",
                          isChecked ? "text-gray-900 font-medium" : "text-gray-700"
                        )}
                      >
                        <div className="flex items-center justify-between">
                          <span>{doc.name}</span>
                          {isChecked && (
                            <Circle className="h-5 w-5 text-blue-600 fill-current" />
                          )}
                        </div>
                        {doc.provided_date && (
                          <p className="text-xs text-gray-500 mt-1">
                            Fornecido em: {new Date(doc.provided_date).toLocaleDateString('pt-BR')}
                          </p>
                        )}
                      </label>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>

        {/* Resumo do Checklist */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="flex items-center justify-between text-sm font-sans">
            <span className="text-gray-600">
              Progresso do Checklist
            </span>
            <span className="font-semibold text-[#1A2B3C]">
              {documents.filter(d => d.provided).length} / {documents.length} documentos
            </span>
          </div>
          <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-[#1A2B3C] transition-all duration-300"
              style={{
                width: `${(documents.filter(d => d.provided).length / documents.length) * 100}%`
              }}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
