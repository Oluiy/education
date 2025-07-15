'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import DashboardLayout from '@/components/layout/DashboardLayout'
import {
  UserIcon,
  KeyIcon,
  BellIcon,
  EyeIcon,
  ShieldCheckIcon,
  GlobeAltIcon,
  DevicePhoneMobileIcon,
  CogIcon,
  CheckIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('profile')
  const [notifications, setNotifications] = useState({
    email: true,
    sms: false,
    push: true,
    assignments: true,
    grades: true,
    announcements: false
  })

  const tabs = [
    { id: 'profile', label: 'Profile', icon: UserIcon },
    { id: 'security', label: 'Security', icon: ShieldCheckIcon },
    { id: 'notifications', label: 'Notifications', icon: BellIcon },
    { id: 'privacy', label: 'Privacy', icon: EyeIcon },
    { id: 'preferences', label: 'Preferences', icon: CogIcon }
  ]

  const handleNotificationChange = (key: string) => {
    setNotifications(prev => ({
      ...prev,
      [key]: !prev[key as keyof typeof prev]
    }))
  }

  return (
    <DashboardLayout userType="student">
      <div className="p-6">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <h1 className="text-2xl font-heading font-bold text-gray-900 mb-2">
              Settings
            </h1>
            <p className="text-gray-600">
              Manage your account settings and preferences
            </p>
          </motion.div>

          <div className="flex flex-col lg:flex-row gap-6">
            {/* Sidebar */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className="lg:w-64 flex-shrink-0"
            >
              <nav className="space-y-1">
                {tabs.map((tab) => {
                  const Icon = tab.icon
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`w-full flex items-center px-4 py-3 text-left rounded-lg transition-colors ${
                        activeTab === tab.id
                          ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-500'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                      }`}
                    >
                      <Icon className="w-5 h-5 mr-3" />
                      {tab.label}
                    </button>
                  )
                })}
              </nav>
            </motion.div>

            {/* Content */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="flex-1"
            >
              {/* Profile Tab */}
              {activeTab === 'profile' && (
                <div className="card">
                  <div className="card-body">
                    <h2 className="font-heading font-semibold text-gray-900 mb-6">
                      Profile Information
                    </h2>
                    
                    <div className="space-y-6">
                      {/* Profile Picture */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Profile Picture
                        </label>
                        <div className="flex items-center space-x-4">
                          <div className="w-20 h-20 bg-gray-300 rounded-full flex items-center justify-center">
                            <UserIcon className="w-10 h-10 text-gray-500" />
                          </div>
                          <div>
                            <button className="btn-secondary btn-sm">Change Photo</button>
                            <p className="text-xs text-gray-500 mt-1">
                              JPG, PNG up to 2MB
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Personal Information */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            First Name
                          </label>
                          <input
                            type="text"
                            defaultValue="John"
                            className="input w-full"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Last Name
                          </label>
                          <input
                            type="text"
                            defaultValue="Doe"
                            className="input w-full"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Email Address
                        </label>
                        <input
                          type="email"
                          defaultValue="john.doe@example.com"
                          className="input w-full"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Phone Number
                        </label>
                        <input
                          type="tel"
                          defaultValue="+234 123 456 7890"
                          className="input w-full"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Bio
                        </label>
                        <textarea
                          rows={4}
                          defaultValue="A dedicated student passionate about learning and academic excellence."
                          className="input w-full"
                        />
                      </div>

                      <div className="flex justify-end">
                        <button className="btn-primary">Save Changes</button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Security Tab */}
              {activeTab === 'security' && (
                <div className="space-y-6">
                  {/* Change Password */}
                  <div className="card">
                    <div className="card-body">
                      <h2 className="font-heading font-semibold text-gray-900 mb-6">
                        Change Password
                      </h2>
                      
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Current Password
                          </label>
                          <input
                            type="password"
                            className="input w-full"
                            placeholder="Enter current password"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            New Password
                          </label>
                          <input
                            type="password"
                            className="input w-full"
                            placeholder="Enter new password"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Confirm New Password
                          </label>
                          <input
                            type="password"
                            className="input w-full"
                            placeholder="Confirm new password"
                          />
                        </div>
                        <button className="btn-primary">Update Password</button>
                      </div>
                    </div>
                  </div>

                  {/* Two-Factor Authentication */}
                  <div className="card">
                    <div className="card-body">
                      <h2 className="font-heading font-semibold text-gray-900 mb-6">
                        Two-Factor Authentication
                      </h2>
                      
                      <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                        <div>
                          <h3 className="font-medium text-gray-900">SMS Authentication</h3>
                          <p className="text-sm text-gray-600">
                            Receive verification codes via SMS
                          </p>
                        </div>
                        <button className="btn-secondary btn-sm">Enable</button>
                      </div>
                    </div>
                  </div>

                  {/* Login Activity */}
                  <div className="card">
                    <div className="card-body">
                      <h2 className="font-heading font-semibold text-gray-900 mb-6">
                        Recent Login Activity
                      </h2>
                      
                      <div className="space-y-4">
                        {[
                          { device: 'Chrome on Windows', location: 'Lagos, Nigeria', time: '2 hours ago', current: true },
                          { device: 'Safari on iPhone', location: 'Lagos, Nigeria', time: '1 day ago', current: false },
                          { device: 'Chrome on Android', location: 'Abuja, Nigeria', time: '3 days ago', current: false }
                        ].map((session, index) => (
                          <div key={index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                            <div className="flex items-center space-x-3">
                              <DevicePhoneMobileIcon className="w-5 h-5 text-gray-400" />
                              <div>
                                <p className="font-medium text-gray-900">{session.device}</p>
                                <p className="text-sm text-gray-600">{session.location} • {session.time}</p>
                              </div>
                            </div>
                            {session.current ? (
                              <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                                Current
                              </span>
                            ) : (
                              <button className="text-red-600 hover:text-red-800 text-sm">
                                End Session
                              </button>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Notifications Tab */}
              {activeTab === 'notifications' && (
                <div className="card">
                  <div className="card-body">
                    <h2 className="font-heading font-semibold text-gray-900 mb-6">
                      Notification Preferences
                    </h2>
                    
                    <div className="space-y-6">
                      {/* Notification Methods */}
                      <div>
                        <h3 className="font-medium text-gray-900 mb-4">Notification Methods</h3>
                        <div className="space-y-3">
                          {[
                            { key: 'email', label: 'Email Notifications', description: 'Receive notifications via email' },
                            { key: 'sms', label: 'SMS Notifications', description: 'Receive notifications via SMS' },
                            { key: 'push', label: 'Push Notifications', description: 'Receive browser push notifications' }
                          ].map((method) => (
                            <div key={method.key} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                              <div>
                                <h4 className="font-medium text-gray-900">{method.label}</h4>
                                <p className="text-sm text-gray-600">{method.description}</p>
                              </div>
                              <button
                                onClick={() => handleNotificationChange(method.key)}
                                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                                  notifications[method.key as keyof typeof notifications]
                                    ? 'bg-primary-600'
                                    : 'bg-gray-200'
                                }`}
                              >
                                <span
                                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                                    notifications[method.key as keyof typeof notifications]
                                      ? 'translate-x-6'
                                      : 'translate-x-1'
                                  }`}
                                />
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Notification Types */}
                      <div>
                        <h3 className="font-medium text-gray-900 mb-4">Notification Types</h3>
                        <div className="space-y-3">
                          {[
                            { key: 'assignments', label: 'New Assignments', description: 'When teachers post new assignments' },
                            { key: 'grades', label: 'Grade Updates', description: 'When grades are posted or updated' },
                            { key: 'announcements', label: 'School Announcements', description: 'Important school-wide announcements' }
                          ].map((type) => (
                            <div key={type.key} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                              <div>
                                <h4 className="font-medium text-gray-900">{type.label}</h4>
                                <p className="text-sm text-gray-600">{type.description}</p>
                              </div>
                              <button
                                onClick={() => handleNotificationChange(type.key)}
                                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                                  notifications[type.key as keyof typeof notifications]
                                    ? 'bg-primary-600'
                                    : 'bg-gray-200'
                                }`}
                              >
                                <span
                                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                                    notifications[type.key as keyof typeof notifications]
                                      ? 'translate-x-6'
                                      : 'translate-x-1'
                                  }`}
                                />
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Privacy Tab */}
              {activeTab === 'privacy' && (
                <div className="space-y-6">
                  <div className="card">
                    <div className="card-body">
                      <h2 className="font-heading font-semibold text-gray-900 mb-6">
                        Privacy Settings
                      </h2>
                      
                      <div className="space-y-4">
                        {[
                          {
                            title: 'Profile Visibility',
                            description: 'Control who can see your profile information',
                            options: ['Public', 'School Only', 'Private']
                          },
                          {
                            title: 'Activity Status',
                            description: 'Show when you were last active',
                            options: ['Everyone', 'Contacts', 'Nobody']
                          },
                          {
                            title: 'Grade Sharing',
                            description: 'Allow parents to view your grades',
                            options: ['Allow', 'Restrict']
                          }
                        ].map((setting, index) => (
                          <div key={index} className="p-4 border border-gray-200 rounded-lg">
                            <h3 className="font-medium text-gray-900 mb-2">{setting.title}</h3>
                            <p className="text-sm text-gray-600 mb-3">{setting.description}</p>
                            <select className="input w-full max-w-xs">
                              {setting.options.map((option) => (
                                <option key={option} value={option.toLowerCase()}>
                                  {option}
                                </option>
                              ))}
                            </select>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="card">
                    <div className="card-body">
                      <h2 className="font-heading font-semibold text-gray-900 mb-6">
                        Data Management
                      </h2>
                      
                      <div className="space-y-4">
                        <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                          <div>
                            <h3 className="font-medium text-gray-900">Download Your Data</h3>
                            <p className="text-sm text-gray-600">Get a copy of all your data</p>
                          </div>
                          <button className="btn-secondary btn-sm">Download</button>
                        </div>
                        
                        <div className="flex items-center justify-between p-4 border border-red-200 rounded-lg bg-red-50">
                          <div>
                            <h3 className="font-medium text-red-900">Delete Account</h3>
                            <p className="text-sm text-red-600">Permanently delete your account and data</p>
                          </div>
                          <button className="btn-sm bg-red-600 text-white hover:bg-red-700">
                            Delete
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Preferences Tab */}
              {activeTab === 'preferences' && (
                <div className="card">
                  <div className="card-body">
                    <h2 className="font-heading font-semibold text-gray-900 mb-6">
                      App Preferences
                    </h2>
                    
                    <div className="space-y-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Language
                        </label>
                        <select className="input w-full max-w-xs">
                          <option>English</option>
                          <option>French</option>
                          <option>Arabic</option>
                          <option>Swahili</option>
                          <option>Hausa</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Time Zone
                        </label>
                        <select className="input w-full max-w-xs">
                          <option>Africa/Lagos (WAT)</option>
                          <option>Africa/Cairo (EET)</option>
                          <option>Africa/Johannesburg (SAST)</option>
                          <option>Africa/Nairobi (EAT)</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Theme
                        </label>
                        <select className="input w-full max-w-xs">
                          <option>Light</option>
                          <option>Dark</option>
                          <option>System</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Date Format
                        </label>
                        <select className="input w-full max-w-xs">
                          <option>DD/MM/YYYY</option>
                          <option>MM/DD/YYYY</option>
                          <option>YYYY-MM-DD</option>
                        </select>
                      </div>

                      <div className="flex justify-end">
                        <button className="btn-primary">Save Preferences</button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
