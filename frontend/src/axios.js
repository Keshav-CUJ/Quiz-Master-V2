import axios from 'axios'

const BACKEND_URL = process.env.VUE_APP_API_URL

const api = axios.create({
  baseURL: BACKEND_URL,
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    // console.log('🔐 Sending token:', token)
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api