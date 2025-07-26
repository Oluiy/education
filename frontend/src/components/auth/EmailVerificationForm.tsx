// src/components/auth/EmailVerificationForm.tsx
'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { verifyEmail } from '@/api/profile'
import { useToast } from '@/contexts/ToastContext'
import { LoadingSpinner } from '@/components/ui/Loading'

export function EmailVerificationForm() {
  const [isLoading, setIsLoading] = useState(true)
  const [isSuccess, setIsSuccess] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()
  const searchParams = useSearchParams()
  const { success: showSuccessToast, error: showErrorToast } = useToast()

  useEffect(() => {
    const token = searchParams.get('token')
    if (!token) {
      setError('Invalid verification link')
      setIsLoading(false)
      return
    }

    const verify = async () => {
      try {
        await verifyEmail(token)
        setIsSuccess(true)
        showSuccessToast('Email verified successfully')
        setTimeout(() => router.push('/login'), 3000)
      } catch (error) {
        setError('Email verification failed')
        showErrorToast('Email verification failed')
      } finally {
        setIsLoading(false)
      }
    }

    verify()
  }, [searchParams, router, showSuccessToast, showErrorToast])

  if (isLoading) {
    return (
      <div className="text-center p-6">
        <LoadingSpinner size="lg" />
        <p className="text-gray-600 mt-4">Verifying your email...</p>
      </div>
    )
  }

  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center p-6"
      >
        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Verification Failed</h2>
        <p className="text-gray-600 mb-4">{error}</p>
        <button
          onClick={() => router.push('/login')}
          className="btn btn-primary"
        >
          Back to Login
        </button>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="text-center p-6"
    >
      <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <h2 className="text-xl font-semibold text-gray-900 mb-2">Email Verified!</h2>
      <p className="text-gray-600">Your email has been successfully verified. Redirecting to login...</p>
    </motion.div>
  )
}
