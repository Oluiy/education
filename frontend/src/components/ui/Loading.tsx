'use client'

import { motion } from 'framer-motion'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  color?: 'primary' | 'secondary' | 'white' | 'gray'
  className?: string
}

export function LoadingSpinner({ 
  size = 'md', 
  color = 'primary', 
  className = '' 
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  }

  const colorClasses = {
    primary: 'border-primary-600 border-t-transparent',
    secondary: 'border-secondary-600 border-t-transparent',
    white: 'border-white border-t-transparent',
    gray: 'border-gray-600 border-t-transparent'
  }

  return (
    <div
      className={`
        ${sizeClasses[size]} 
        ${colorClasses[color]}
        border-2 rounded-full animate-spin
        ${className}
      `}
    />
  )
}

interface LoadingSkeletonProps {
  rows?: number
  className?: string
  avatar?: boolean
}

export function LoadingSkeleton({ 
  rows = 3, 
  className = '',
  avatar = false 
}: LoadingSkeletonProps) {
  return (
    <div className={`animate-pulse ${className}`}>
      {avatar && (
        <div className="flex items-center space-x-4 mb-4">
          <div className="w-12 h-12 bg-gray-300 rounded-full" />
          <div className="space-y-2 flex-1">
            <div className="h-4 bg-gray-300 rounded w-1/4" />
            <div className="h-3 bg-gray-300 rounded w-1/2" />
          </div>
        </div>
      )}
      
      <div className="space-y-3">
        {Array.from({ length: rows }).map((_, index) => (
          <div key={index} className="space-y-3">
            <div className="h-4 bg-gray-300 rounded" />
            <div className="h-4 bg-gray-300 rounded w-5/6" />
            {index < rows - 1 && <div className="h-4 bg-gray-300 rounded w-4/6" />}
          </div>
        ))}
      </div>
    </div>
  )
}

interface CardSkeletonProps {
  count?: number
  className?: string
}

export function CardSkeleton({ count = 1, className = '' }: CardSkeletonProps) {
  return (
    <div className={`grid gap-6 ${className}`}>
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="animate-pulse">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-4 mb-4">
              <div className="w-12 h-12 bg-gray-300 rounded-lg" />
              <div className="space-y-2 flex-1">
                <div className="h-4 bg-gray-300 rounded w-1/3" />
                <div className="h-3 bg-gray-300 rounded w-1/2" />
              </div>
            </div>
            <div className="space-y-3">
              <div className="h-4 bg-gray-300 rounded" />
              <div className="h-4 bg-gray-300 rounded w-4/5" />
              <div className="h-4 bg-gray-300 rounded w-3/5" />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

interface TableSkeletonProps {
  rows?: number
  columns?: number
  className?: string
}

export function TableSkeleton({ 
  rows = 5, 
  columns = 4, 
  className = '' 
}: TableSkeletonProps) {
  return (
    <div className={`animate-pulse ${className}`}>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        {/* Header */}
        <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
          <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
            {Array.from({ length: columns }).map((_, index) => (
              <div key={index} className="h-4 bg-gray-300 rounded" />
            ))}
          </div>
        </div>
        
        {/* Rows */}
        <div className="divide-y divide-gray-200">
          {Array.from({ length: rows }).map((_, rowIndex) => (
            <div key={rowIndex} className="px-6 py-4">
              <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
                {Array.from({ length: columns }).map((_, colIndex) => (
                  <div key={colIndex} className="h-4 bg-gray-300 rounded" />
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

interface LoadingPageProps {
  title?: string
  description?: string
}

export function LoadingPage({ 
  title = "Loading...", 
  description = "Please wait while we load your content" 
}: LoadingPageProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <LoadingSpinner size="xl" className="mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">{title}</h2>
        <p className="text-gray-600">{description}</p>
      </motion.div>
    </div>
  )
}

interface LoadingOverlayProps {
  isVisible: boolean
  message?: string
}

export function LoadingOverlay({ 
  isVisible, 
  message = "Loading..." 
}: LoadingOverlayProps) {
  if (!isVisible) return null

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div className="bg-white rounded-lg p-6 shadow-xl">
        <div className="flex items-center space-x-3">
          <LoadingSpinner size="md" />
          <span className="text-gray-900 font-medium">{message}</span>
        </div>
      </div>
    </motion.div>
  )
}
