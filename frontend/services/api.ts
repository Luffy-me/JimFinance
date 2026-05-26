import axios, { AxiosInstance, AxiosError } from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

export class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor to add auth token
    this.client.interceptors.request.use((config) => {
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
      if (token) {
        config.headers.Authorization = 'Bearer ' + token
      }
      return config
    })

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          if (typeof window !== 'undefined') {
            localStorage.removeItem('access_token')
            window.location.href = '/login'
          }
        }
        return Promise.reject(error)
      }
    )
  }

  async register(email: string, password: string, name: string) {
    const response = await this.client.post('/auth/register', { email, password, name })
    return response.data
  }

  async login(email: string, password: string) {
    const response = await this.client.post('/auth/login', { email, password })
    return response.data
  }

  async logout() {
    const response = await this.client.post('/auth/logout')
    return response.data
  }

  async getCurrentUser() {
    const response = await this.client.get('/users/me')
    return response.data
  }

  async updateUserProfile(data: any) {
    const response = await this.client.put('/users/me', data)
    return response.data
  }

  async getAccounts() {
    const response = await this.client.get('/accounts')
    return response.data
  }

  async createAccount(data: any) {
    const response = await this.client.post('/accounts', data)
    return response.data
  }

  async updateAccount(id: string, data: any) {
    const response = await this.client.put(`/accounts/${id}`, data)
    return response.data
  }

  async deleteAccount(id: string) {
    const response = await this.client.delete(`/accounts/${id}`)
    return response.data
  }

  async getTransactions(params?: any) {
    const response = await this.client.get('/transactions', { params })
    return response.data
  }

  async createTransaction(data: any) {
    const response = await this.client.post('/transactions', data)
    return response.data
  }

  async updateTransaction(id: string, data: any) {
    const response = await this.client.put(`/transactions/${id}`, data)
    return response.data
  }

  async deleteTransaction(id: string) {
    const response = await this.client.delete(`/transactions/${id}`)
    return response.data
  }

  async getCategories() {
    const response = await this.client.get('/categories')
    return response.data
  }

  async createCategory(data: any) {
    const response = await this.client.post('/categories', data)
    return response.data
  }

  async deleteCategory(id: string) {
    const response = await this.client.delete(`/categories/${id}`)
    return response.data
  }

  async getSubscriptions() {
    const response = await this.client.get('/subscriptions')
    return response.data
  }

  async createSubscription(data: any) {
    const response = await this.client.post('/subscriptions', data)
    return response.data
  }

  async updateSubscription(id: string, data: any) {
    const response = await this.client.put(`/subscriptions/${id}`, data)
    return response.data
  }

  async deleteSubscription(id: string) {
    const response = await this.client.delete(`/subscriptions/${id}`)
    return response.data
  }

  async getDashboardStats() {
    const response = await this.client.get('/dashboard')
    return response.data
  }

  async classifyTransaction(data: any) {
    const response = await this.client.post('/intelligence/classify', data)
    return response.data
  }

  async detectAnomalies(params?: any) {
    const response = await this.client.post('/intelligence/anomaly', {}, { params })
    return response.data
  }

  async getRecurringTransactions(params?: any) {
    const response = await this.client.post('/intelligence/recurring', {}, { params })
    return response.data
  }
}

export const apiClient = new ApiClient()
