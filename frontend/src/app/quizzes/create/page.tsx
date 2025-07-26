// src/app/quizzes/create/page.tsx
'use client'

import { useRouter } from 'next/navigation'
import { QuizBuilder } from '@/components/quizzes/QuizBuilder'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/contexts/ToastContext'
import { useEffect } from 'react'

export default function CreateQuizPage() {
  const router = useRouter()
  const { user } = useAuth()
  const { error } = useToast()

  useEffect(() => {
    if (user && user.role !== 'teacher' && user.role !== 'admin') {
      error('You do not have permission to create quizzes')
      router.push('/quizzes')
    }
  }, [user, router, error])

  if (!user || (user.role !== 'teacher' && user.role !== 'admin')) {
    return null
  }

  const handleSave = () => {
    router.push('/quizzes')
  }

  const handleCancel = () => {
    router.push('/quizzes')
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <QuizBuilder
        onSave={handleSave}
        onCancel={handleCancel}
      />
    </div>
  )
}
