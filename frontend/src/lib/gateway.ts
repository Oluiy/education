// API Gateway configuration for EduNerve microservices
import { api, apiRequest, getAuthToken } from './api'

// API URLs from api.ts
const API_URLS = {
  AUTH: process.env.NEXT_PUBLIC_AUTH_URL || 'http://localhost:8001',
  CONTENT: process.env.NEXT_PUBLIC_CONTENT_URL || 'http://localhost:8002',
  ASSISTANT: process.env.NEXT_PUBLIC_ASSISTANT_URL || 'http://localhost:8003',
  ADMIN: process.env.NEXT_PUBLIC_ADMIN_URL || 'http://localhost:8004',
  NOTIFICATIONS: process.env.NEXT_PUBLIC_NOTIFICATION_URL || 'http://localhost:8006',
  FILES: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
}
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination?: {
    page: number
    limit: number
    total: number
    totalPages: number
  }
}

// Service health check
export const checkServiceHealth = async (service: keyof typeof API_URLS): Promise<boolean> => {
  try {
    const response = await fetch(`${API_URLS[service]}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    return response.ok
  } catch (error) {
    console.error(`Service ${service} health check failed:`, error)
    return false
  }
}

// Retry mechanism for failed requests
export const retryRequest = async <T>(
  requestFn: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> => {
  let lastError: Error
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn()
    } catch (error) {
      lastError = error as Error
      if (i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, delay * (i + 1)))
      }
    }
  }
  
  throw lastError!
}

// Circuit breaker for service failures
class CircuitBreaker {
  private failureCount = 0
  private nextAttempt = 0
  private state: 'closed' | 'open' | 'half-open' = 'closed'
  
  constructor(
    private threshold: number = 5,
    private timeout: number = 60000 // 1 minute
  ) {}
  
  async call<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === 'open') {
      if (Date.now() < this.nextAttempt) {
        throw new Error('Circuit breaker is open')
      }
      this.state = 'half-open'
    }
    
    try {
      const result = await fn()
      this.reset()
      return result
    } catch (error) {
      this.recordFailure()
      throw error
    }
  }
  
  private recordFailure() {
    this.failureCount++
    if (this.failureCount >= this.threshold) {
      this.state = 'open'
      this.nextAttempt = Date.now() + this.timeout
    }
  }
  
  private reset() {
    this.failureCount = 0
    this.state = 'closed'
    this.nextAttempt = 0
  }
}

// Create circuit breakers for each service
const circuitBreakers = {
  AUTH: new CircuitBreaker(),
  CONTENT: new CircuitBreaker(),
  ASSISTANT: new CircuitBreaker(),
  ADMIN: new CircuitBreaker(),
  NOTIFICATIONS: new CircuitBreaker(),
  FILES: new CircuitBreaker(),
}

// Enhanced API request with circuit breaker and retry
export const robustApiRequest = async (
  service: keyof typeof API_URLS,
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> => {
  const circuitBreaker = circuitBreakers[service]
  
  return circuitBreaker.call(async () => {
    return retryRequest(async () => {
      return apiRequest(service, endpoint, options)
    })
  })
}

// Batch request handling
export const batchRequest = async (
  requests: Array<{
    service: keyof typeof API_URLS
    endpoint: string
    options?: RequestInit
  }>
): Promise<Response[]> => {
  return Promise.all(
    requests.map(({ service, endpoint, options }) =>
      robustApiRequest(service, endpoint, options)
    )
  )
}

// WebSocket connection for real-time updates
export class RealtimeConnection {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  
  constructor(private url: string) {}
  
  connect(onMessage: (data: any) => void, onError?: (error: Event) => void) {
    try {
      const token = getAuthToken()
      const wsUrl = `${this.url}?token=${token}`
      
      this.ws = new WebSocket(wsUrl)
      
      this.ws.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
      }
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          onMessage(data)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }
      
      this.ws.onclose = () => {
        console.log('WebSocket disconnected')
        this.handleReconnect(onMessage, onError)
      }
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        if (onError) onError(error)
      }
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
      if (onError) onError(error as Event)
    }
  }
  
  private handleReconnect(onMessage: (data: any) => void, onError?: (error: Event) => void) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      setTimeout(() => {
        console.log(`Attempting to reconnect WebSocket (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
        this.connect(onMessage, onError)
      }, this.reconnectDelay * this.reconnectAttempts)
    }
  }
  
  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }
  
  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}

// Export enhanced API instance
export const enhancedApi = {
  ...api,
  health: {
    checkAll: async () => {
      const services = Object.keys(API_URLS) as Array<keyof typeof API_URLS>
      const results = await Promise.allSettled(
        services.map(async (service) => ({
          service,
          healthy: await checkServiceHealth(service)
        }))
      )
      
      return results.map((result, index) => ({
        service: services[index],
        healthy: result.status === 'fulfilled' ? result.value.healthy : false
      }))
    }
  },
  realtime: {
    connect: (url: string) => new RealtimeConnection(url),
  }
}

export default enhancedApi
