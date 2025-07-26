// src/components/auth/PasswordResetForm.tsx
'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { requestPasswordReset } from '../../api/profile'
import { useToast } from '../../contexts/ToastContext'
import { LoadingSpinner } from '../../components/ui/Loading'

const emailSchema = z.object({
  email: z.string().min(1, 'Email is required').email('Invalid email format')
})

type EmailFormData = z.infer<typeof emailSchema>

export function PasswordResetForm() {
  const [isLoading, setIsLoading] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)
  const { success: showSuccessToast, error: showErrorToast } = useToast()

  const {
    register,
    handleSubmit,
    formState: { errors, isValid }
  } = useForm<EmailFormData>({
    resolver: zodResolver(emailSchema),
    mode: 'onChange'
  })

  const onSubmit = async (formData: EmailFormData) => {
    setIsLoading(true)
    try {
      await requestPasswordReset(formData.email)
      setIsSuccess(true)
      showSuccessToast('Password reset email sent successfully')
    } catch (error) {
      showErrorToast('Failed to send password reset email')
    } finally {
      setIsLoading(false)
    }
  }

  if (isSuccess) {
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
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Check Your Email</h2>
        <p className="text-gray-600">We've sent a password reset link to your email</p>
      </motion.div>
    )
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label htmlFor="email" className="label">Email Address</label>
        <input
          type="email"
          id="email"
          className={`input ${errors.email ? 'input-error' : ''}`}
          placeholder="Enter your email"
          {...register('email')}
          disabled={isLoading}
        />
        {errors.email && <p className="text-red-600 text-sm mt-1">{errors.email.message}</p>}
      </div>

      <button
        type="submit"
        disabled={!isValid || isLoading}
        className="btn btn-primary w-full"
      >
        {isLoading ? <LoadingSpinner size="sm" /> : 'Send Reset Link'}
      </button>
    </form>
  )
}
