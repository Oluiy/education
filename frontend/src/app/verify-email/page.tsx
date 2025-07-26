// src/app/verify-email/page.tsx
'use client'

import { Suspense } from 'react'
import { motion } from 'framer-motion'
import { EmailVerificationForm } from '@/components/auth/EmailVerificationForm'
import { LoadingSpinner } from '@/components/ui/Loading'

function VerifyEmailContent() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Email Verification</h1>
          </div>

          <EmailVerificationForm />
        </div>
      </motion.div>
    </div>
  )
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    }>
      <VerifyEmailContent />
    </Suspense>
  )
}
