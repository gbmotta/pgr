import { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'
import { API_URL } from '@/lib/apiConfig'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Verificar token salvo
    const token = localStorage.getItem('token')
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      fetchUser()
    } else {
      setLoading(false)
    }
  }, [])

  const fetchUser = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/auth/me`)
      setUser(response.data)
    } catch (error) {
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
    } finally {
      setLoading(false)
    }
  }

  /** Atualiza o objeto `user` sem desligar o loading inicial (útil após guardar perfil). */
  const refreshUser = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/auth/me`)
      setUser(response.data)
    } catch {
      /* ignorar; sessão pode ter expirado */
    }
  }

  const login = async (username, password) => {
    const response = await axios.post(`${API_URL}/api/auth/login`, {
      username,
      password,
    })
    const { access_token, user: userData } = response.data
    localStorage.setItem('token', access_token)
    axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
    setUser(userData)
    return userData
  }

  const logout = () => {
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, loading, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

