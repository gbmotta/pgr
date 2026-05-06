import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { 
  ArrowLeft,
  Clock,
  CheckCircle,
  FileText
} from 'lucide-react'
import DocumentChecklist from '../components/DocumentChecklist'
import { API_URL } from '@/lib/apiConfig'

/**
 * Componente Timeline para exibir eventos do processo
 */
function TimelineItem({ event, isLast = false }) {
  return (
    <div className="relative flex items-start">
      {/* Linha vertical */}
      {!isLast && (
        <div className="absolute left-4 top-8 w-0.5 h-full bg-gray-300"></div>
      )}
      
      {/* Círculo azul */}
      <div className="relative z-10 flex items-center justify-center w-8 h-8 rounded-full bg-blue-600 border-4 border-white shadow-sm">
        <div className="w-2 h-2 rounded-full bg-white"></div>
      </div>
      
      {/* Conteúdo do evento */}
      <div className="ml-4 pb-8 flex-1">
        <h3 className="text-base font-semibold text-gray-900 font-sans">
          {event.title}
        </h3>
        {event.date && (
          <p className="mt-1 text-sm text-gray-600 font-sans">
            {event.date}
          </p>
        )}
        {event.description && (
          <p className="mt-2 text-sm text-gray-500 font-sans">
            {event.description}
          </p>
        )}
      </div>
    </div>
  )
}

export default function ProcessDetail() {
  const { protocol } = useParams()
  const navigate = useNavigate()

  const { data: process, isLoading } = useQuery({
    queryKey: ['process', protocol],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/processes/${protocol}`)
      return response.data
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#1A2B3C]"></div>
      </div>
    )
  }

  if (!process) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <p className="text-lg font-medium text-gray-900 font-sans">Processo não encontrado</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="mt-4 text-sm text-blue-600 hover:text-blue-800 font-sans"
          >
            Voltar para o Dashboard
          </button>
        </div>
      </div>
    )
  }

  // Preparar eventos da timeline
  const timelineEvents = []

  // Evento: Recebimento
  if (process.created_date || process.data_recebimento_mes_ano) {
    const recebimentoDate = process.data_recebimento_mes_ano 
      ? process.data_recebimento_mes_ano 
      : process.created_date
        ? format(new Date(process.created_date), "dd 'de' MMMM 'de' yyyy", { locale: ptBR })
        : null

    timelineEvents.push({
      title: 'Recebimento',
      date: recebimentoDate,
      description: 'Processo recebido no sistema',
      icon: FileText
    })
  }

  // Evento: Análise de Prazo
  if (process.prazo_final || process.prazo_info_estag) {
    const prazoDate = process.prazo_final || process.prazo_info_estag
    timelineEvents.push({
      title: 'Análise de Prazo',
      date: prazoDate ? `Prazo: ${prazoDate}` : null,
      description: 'Prazo definido para análise do processo',
      icon: Clock
    })
  }

  // Evento: Conclusão
  if (process.data_realizacao_ato || process.closed_date) {
    let conclusaoDate = null
    
    if (process.data_realizacao_ato) {
      // Tentar parsear data no formato DD/MM/AAAA ou Date
      try {
        if (process.data_realizacao_ato.includes('/')) {
          // Formato DD/MM/AAAA
          const [day, month, year] = process.data_realizacao_ato.split('/').map(Number)
          conclusaoDate = format(new Date(year, month - 1, day), "dd 'de' MMMM 'de' yyyy", { locale: ptBR })
        } else {
          // Formato ISO Date
          conclusaoDate = format(new Date(process.data_realizacao_ato), "dd 'de' MMMM 'de' yyyy", { locale: ptBR })
        }
      } catch {
        conclusaoDate = process.data_realizacao_ato
      }
    } else if (process.closed_date) {
      conclusaoDate = format(new Date(process.closed_date), "dd 'de' MMMM 'de' yyyy", { locale: ptBR })
    }

    timelineEvents.push({
      title: 'Conclusão',
      date: conclusaoDate,
      description: process.tipo_ato || 'Processo concluído',
      icon: CheckCircle
    })
  }

  // Se não houver eventos, adicionar pelo menos o recebimento
  if (timelineEvents.length === 0) {
    timelineEvents.push({
      title: 'Recebimento',
      date: process.created_date 
        ? format(new Date(process.created_date), "dd 'de' MMMM 'de' yyyy", { locale: ptBR })
        : null,
      description: 'Processo registrado no sistema',
      icon: FileText
    })
  }

  return (
    <div className="space-y-6">
      {/* Botão Voltar */}
      <button
        onClick={() => navigate('/dashboard')}
        className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 font-sans"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        Voltar
      </button>

      {/* Layout: Card à esquerda e Timeline à direita */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Card Branco - Dados Principais (Lado Esquerdo) */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-serif font-bold text-gray-900 mb-6">
            Dados do Processo
          </h2>
          
          <div className="space-y-6">
            {/* Número do Processo */}
            <div>
              <h3 className="text-sm font-medium text-gray-500 font-sans uppercase tracking-wide mb-2">
                Número
              </h3>
              <p className="text-lg font-semibold text-gray-900 font-sans">
                {process.processo_adm_1doc || process.processo_judicial || process.protocol_number || 'N/A'}
              </p>
              {process.processo_judicial && process.processo_adm_1doc && (
                <p className="text-sm text-gray-600 font-sans mt-1">
                  Judicial: {process.processo_judicial}
                </p>
              )}
            </div>

            {/* Juízo */}
            <div>
              <h3 className="text-sm font-medium text-gray-500 font-sans uppercase tracking-wide mb-2">
                Juízo
              </h3>
              <p className="text-base text-gray-900 font-sans">
                {process.tipo_ato || 'Não informado'}
              </p>
            </div>

            {/* Partes */}
            <div>
              <h3 className="text-sm font-medium text-gray-500 font-sans uppercase tracking-wide mb-2">
                Partes
              </h3>
              <p className="text-base text-gray-900 font-sans whitespace-pre-wrap">
                {process.partes || 'Não informado'}
              </p>
            </div>

            {/* Informações Adicionais */}
            {(process.tema_observacoes || process.data_recebimento_mes_ano) && (
              <div className="pt-4 border-t border-gray-200 space-y-4">
                {process.tema_observacoes && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 font-sans uppercase tracking-wide mb-2">
                      Tema / Observações
                    </h3>
                    <p className="text-sm text-gray-700 font-sans whitespace-pre-wrap">
                      {process.tema_observacoes}
                    </p>
                  </div>
                )}
                
                {process.data_recebimento_mes_ano && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 font-sans uppercase tracking-wide mb-2">
                      Data de Recebimento
                    </h3>
                    <p className="text-sm text-gray-700 font-sans">
                      {process.data_recebimento_mes_ano}
                    </p>
                  </div>
                )}

                {process.prazo_final && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 font-sans uppercase tracking-wide mb-2">
                      Prazo Final
                    </h3>
                    <p className="text-sm text-gray-700 font-sans">
                      {process.prazo_final}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Timeline Vertical (Lado Direito) */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-serif font-bold text-gray-900 mb-6">
            Linha do Tempo
          </h2>
          
          <div className="relative">
            {timelineEvents.map((event, index) => (
              <TimelineItem
                key={index}
                event={event}
                isLast={index === timelineEvents.length - 1}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Checklist de Documentos */}
      {process.documents && process.documents.length > 0 && (
        <DocumentChecklist
          processProtocol={protocol}
          documents={process.documents}
        />
      )}
    </div>
  )
}
