// src/app/profile/settings/page.tsx
'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useAuth } from '../../../contexts/AuthContext'
import { useApi } from '../../../hooks/useApi'
import { useToast } from '../../../contexts/ToastContext'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  UserIcon,
  KeyIcon,
  BellIcon,
  ShieldCheckIcon,
  EyeIcon,
  EyeSlashIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

const passwordSchema = z.object({
  currentPassword: z.string().min(1, 'Current password is required'),
  newPassword: z.string().min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string().min(1, 'Please confirm your password')
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"]
})

type PasswordFormData = z.infer<typeof passwordSchema>

export default function ProfileSettingsPage() {
  const [activeTab, setActiveTab] = useState<'account' | 'password' | 'notifications' | 'privacy'>('account')
  const [showCurrentPassword, setShowCurrentPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const { user } = useAuth()
  const { 
    updateProfile, 
    changePassword, 
    deleteAccount,
    useNotificationSettings,
    updateNotificationSettings 
  } = useApi()
  
  const { success, error } = useToast()

  const { data: notificationSettings } = useNotificationSettings(user?.id)

  const passwordForm = useForm<PasswordFormData>({
    resolver: zodResolver(passwordSchema)
  })

  const handlePasswordChange = async (data: PasswordFormData) => {
    try {
      await changePassword.mutateAsync({
        currentPassword: data.currentPassword,
        newPassword: data.newPassword
      })
      success('Password changed successfully')
      passwordForm.reset()
    } catch (err) {
      error(
        `Failed to change password: ${err instanceof Error ? err.message : 'Unknown error'}`
      )
    }
  }

  const handleDeleteAccount = async () => {
    const confirmed = window.confirm(
      'Are you sure you want to delete your account? This action cannot be undone and all your data will be permanently lost.'
    )
    
    if (confirmed) {
      const doubleConfirmed = window.prompt(
        'Type "DELETE" to confirm account deletion:'
      )
      
      if (doubleConfirmed === 'DELETE') {
        try {
          await deleteAccount.mutateAsync(user?.id!)
          success('Account deleted successfully')
        } catch (err) {
          error(
            `Failed to delete account: ${err instanceof Error ? err.message : 'Unknown error'}`
          )
        }
      }
    }
  }

  const toggleNotificationSetting = async (key: string, value: boolean) => {
    try {
      await updateNotificationSettings.mutateAsync({
        userId: user?.id!,
        settings: {
          ...notificationSettings,
          [key]: value
        }
      })
      success('Notification settings updated')
    } catch (err) {
      error('Failed to update notification settings')
    }
  }

  const tabs = [
    { id: 'account', label: 'Account', icon: UserIcon },
    { id: 'password', label: 'Password', icon: KeyIcon },
    { id: 'notifications', label: 'Notifications', icon: BellIcon },
    { id: 'privacy', label: 'Privacy & Security', icon: ShieldCheckIcon }
  ]

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-gray-600">Please log in to access settings</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-2">Manage your account settings and preferences</p>
      </div>

      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="flex border-b border-gray-200">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex-1 flex items-center justify-center space-x-2 py-4 px-6 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'border-b-2 border-blue-500 text-blue-600 bg-blue-50'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        <div className="p-8">
          {/* Account Tab */}
          {activeTab === 'account' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Account Information</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      First Name
                    </label>
                    <input
                      type="text"
                      value={user.firstName}
                      readOnly
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Last Name
                    </label>
                    <input
                      type="text"
                      value={user.lastName}
                      readOnly
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email
                    </label>
                    <input
                      type="email"
                      value={user.email}
                      readOnly
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Role
                    </label>
                    <input
                      type="text"
                      value={user.role}
                      readOnly
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500 capitalize"
                    />
                  </div>
                </div>
                
                <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-blue-800">
                    To update your account information, please contact your administrator or visit your profile page.
                  </p>
                </div>
              </div>
            </motion.div>
          )}

          {/* Password Tab */}
          {activeTab === 'password' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Change Password</h2>
                
                <form onSubmit={passwordForm.handleSubmit(handlePasswordChange)} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Current Password
                    </label>
                    <div className="relative">
                      <input
                        type={showCurrentPassword ? 'text' : 'password'}
                        {...passwordForm.register('currentPassword')}
                        className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <button
                        type="button"
                        onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                        className="absolute inset-y-0 right-0 pr-3 flex items-center"
                      >
                        {showCurrentPassword ? (
                          <EyeSlashIcon className="w-4 h-4 text-gray-400" />
                        ) : (
                          <EyeIcon className="w-4 h-4 text-gray-400" />
                        )}
                      </button>
                    </div>
                    {passwordForm.formState.errors.currentPassword && (
                      <p className="text-red-500 text-sm mt-1">
                        {passwordForm.formState.errors.currentPassword.message}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      New Password
                    </label>
                    <div className="relative">
                      <input
                        type={showNewPassword ? 'text' : 'password'}
                        {...passwordForm.register('newPassword')}
                        className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <button
                        type="button"
                        onClick={() => setShowNewPassword(!showNewPassword)}
                        className="absolute inset-y-0 right-0 pr-3 flex items-center"
                      >
                        {showNewPassword ? (
                          <EyeSlashIcon className="w-4 h-4 text-gray-400" />
                        ) : (
                          <EyeIcon className="w-4 h-4 text-gray-400" />
                        )}
                      </button>
                    </div>
                    {passwordForm.formState.errors.newPassword && (
                      <p className="text-red-500 text-sm mt-1">
                        {passwordForm.formState.errors.newPassword.message}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Confirm New Password
                    </label>
                    <div className="relative">
                      <input
                        type={showConfirmPassword ? 'text' : 'password'}
                        {...passwordForm.register('confirmPassword')}
                        className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="absolute inset-y-0 right-0 pr-3 flex items-center"
                      >
                        {showConfirmPassword ? (
                          <EyeSlashIcon className="w-4 h-4 text-gray-400" />
                        ) : (
                          <EyeIcon className="w-4 h-4 text-gray-400" />
                        )}
                      </button>
                    </div>
                    {passwordForm.formState.errors.confirmPassword && (
                      <p className="text-red-500 text-sm mt-1">
                        {passwordForm.formState.errors.confirmPassword.message}
                      </p>
                    )}
                  </div>

                  <button
                    type="submit"
                    disabled={changePassword.isPending}
                    className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                  >
                    {changePassword.isPending ? 'Changing Password...' : 'Change Password'}
                  </button>
                </form>
              </div>
            </motion.div>
          )}

          {/* Notifications Tab */}
          {activeTab === 'notifications' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Notification Preferences</h2>
                
                {notificationSettings && (
                  <div className="space-y-4">
                    {[
                      {
                        key: 'emailNotifications',
                        title: 'Email Notifications',
                        description: 'Receive notifications via email'
                      },
                      {
                        key: 'pushNotifications',
                        title: 'Push Notifications',
                        description: 'Receive browser push notifications'
                      },
                      {
                        key: 'quizReminders',
                        title: 'Quiz Reminders',
                        description: 'Get reminded about upcoming quiz deadlines'
                      },
                      {
                        key: 'courseUpdates',
                        title: 'Course Updates',
                        description: 'Notifications about course content changes'
                      },
                      {
                        key: 'announcements',
                        title: 'Announcements',
                        description: 'Important announcements from instructors'
                      },
                      {
                        key: 'gradeUpdates',
                        title: 'Grade Updates',
                        description: 'Notifications when assignments are graded'
                      }
                    ].map((setting) => (
                      <div key={setting.key} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                        <div>
                          <h3 className="font-medium text-gray-900">{setting.title}</h3>
                          <p className="text-sm text-gray-600">{setting.description}</p>
                        </div>
                        
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={notificationSettings[setting.key] || false}
                            onChange={(e) => toggleNotificationSetting(setting.key, e.target.checked)}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600" />
                        </label>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {/* Privacy Tab */}
          {activeTab === 'privacy' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Privacy & Security</h2>
                
                <div className="space-y-6">
                  <div className="p-4 border border-gray-200 rounded-lg">
                    <h3 className="font-medium text-gray-900 mb-2">Data Privacy</h3>
                    <p className="text-sm text-gray-600 mb-4">
                      Your personal information is protected and only used for educational purposes within this platform.
                    </p>
                    <button className="text-sm text-blue-600 hover:text-blue-700">
                      View Privacy Policy
                    </button>
                  </div>

                  <div className="p-4 border border-gray-200 rounded-lg">
                    <h3 className="font-medium text-gray-900 mb-2">Download Your Data</h3>
                    <p className="text-sm text-gray-600 mb-4">
                      Request a copy of all your data stored on our platform.
                    </p>
                    <button className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 text-sm">
                      Request Data Export
                    </button>
                  </div>

                  <div className="p-4 border border-red-200 rounded-lg bg-red-50">
                    <div className="flex items-start space-x-3">
                      <ExclamationTriangleIcon className="w-5 h-5 text-red-600 mt-0.5" />
                      <div className="flex-1">
                        <h3 className="font-medium text-red-900 mb-2">Delete Account</h3>
                        <p className="text-sm text-red-700 mb-4">
                          Permanently delete your account and all associated data. This action cannot be undone.
                        </p>
                        <button
                          onClick={handleDeleteAccount}
                          disabled={deleteAccount.isPending}
                          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 text-sm"
                        >
                          {deleteAccount.isPending ? 'Deleting...' : 'Delete Account'}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
}
