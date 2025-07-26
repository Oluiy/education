// src/app/forgot-password/page.tsx
'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { PasswordResetForm } from '@/components/auth/PasswordResetForm'

export default function ForgotPasswordPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Reset Password</h1>
            <p className="text-gray-600">Enter your email to receive a reset link</p>
          </div>

          <PasswordResetForm />

          <div className="text-center mt-6">
            <Link href="/login" className="text-primary-600 hover:text-primary-700 text-sm">
              Back to Login
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
