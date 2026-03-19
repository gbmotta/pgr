import { Calendar as CalendarIcon } from 'lucide-react'

export default function Calendar() {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
        <CalendarIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 font-sans mb-2">
          Calendário de Processos
        </h2>
        <p className="text-gray-600 font-sans">
          Funcionalidade de calendário em desenvolvimento
        </p>
      </div>
    </div>
  )
}
