import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import DashboardNew from './pages/DashboardInstitutional'
import DashboardPerformance from './pages/DashboardPerformance'
import ProcessDetail from './pages/ProcessDetail'
import UploadProcesses from './pages/UploadProcesses'
import Reports from './pages/Reports'
import Calendar from './pages/Calendar'
import Settings from './pages/Settings'
import LinkedSheets from './pages/LinkedSheets'
import Layout from './components/layout/MainLayout'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<DashboardNew />} />
              <Route path="performance" element={<DashboardPerformance />} />
              <Route path="process/:protocol" element={<ProcessDetail />} />
              <Route path="upload" element={<UploadProcesses />} />
              <Route path="linked-sheets" element={<LinkedSheets />} />
              <Route path="reports" element={<Reports />} />
              <Route path="calendar" element={<Calendar />} />
              <Route path="settings" element={<Settings />} />
            </Route>
          </Routes>
        </BrowserRouter>
        <Toaster position="top-right" />
      </AuthProvider>
    </QueryClientProvider>
  )
}

export default App

