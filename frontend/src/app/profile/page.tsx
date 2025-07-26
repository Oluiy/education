// src/app/profile/page.tsx
'use client'

import { useAuth } from '@/contexts/AuthContext'
import { ProfileHeader } from '@/components/profile/ProfileHeader'
import { ProfileStats } from '@/components/profile/ProfileStats'
import { ProfileActivity } from '@/components/profile/ProfileActivity'
import { LoadingSpinner } from '../../components/ui/LoadingSpinner'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export default function ProfilePage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/auth/login')
    }
  }, [user, isLoading, router])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="space-y-8">
        <ProfileHeader user={user} isOwnProfile />
        <ProfileStats user={user} />
        <ProfileActivity user={user} />
      </div>
    </div>
  )
}
