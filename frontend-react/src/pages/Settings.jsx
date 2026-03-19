import { Settings as SettingsIcon } from 'lucide-react'

export default function Settings() {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
        <SettingsIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 font-sans mb-2">
          Configurações
        </h2>
        <p className="text-gray-600 font-sans">
          Página de configurações em desenvolvimento
        </p>
      </div>
    </div>
  )
}
