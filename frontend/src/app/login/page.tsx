'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline'
import { useFormValidation, validationHelpers } from 'src/lib/useFormValidation'
import { useAuth } from '@/contexts/AuthContext'
import { LoadingSpinner } from '@/components/ui/Loading'
import { ErrorAlert } from '@/components/ui/Error'

interface LoginForm {
  email: string
  password: string
  rememberMe: boolean
}

export default function LoginPage() {
  const router = useRouter()
  const { login, user } = useAuth()
  const [showPassword, setShowPassword] = useState(false)
  const [apiError, setApiError] = useState('')

  // Redirect based on user role after successful login
  useEffect(() => {
    if (user) {
      switch (user.role) {
        case 'teacher':
          router.push('/teacher/dashboard')
          break
        case 'student':
          router.push('/student/dashboard')
          break
        case 'parent':
          router.push('/parent/dashboard')
          break
        case 'admin':
          router.push('/admin/dashboard')
          break
        default:
          router.push('/dashboard')
      }
    }
  }, [user, router])

  const {
    values,
    errors,
    isSubmitting,
    handleChange,
    handleSubmit,
    setErrors
  } = useFormValidation<LoginForm>({
    initialValues: {
      email: '',
      password: '',
      rememberMe: false
    },
    validationRules: {
      email: {
        required: true,
        custom: validationHelpers.email
      },
      password: {
        required: true,
        minLength: 6
      }
    },
    onSubmit: async (formData: LoginForm) => {
      try {
        setApiError('')
        await login(formData.email, formData.password)
        
        // The AuthContext should set the user state after successful login
        // We'll redirect based on user role in useEffect below
      } catch (error: any) {
        console.error('Login error:', error)
        setApiError(error.message || 'Login failed. Please check your credentials.')
      }
    }
  })

  return (
    <div className="min-h-screen flex">
      {/* Left side - Login form */}
      <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8">
        <motion.div 
          className="w-full max-w-xl space-y-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* Header */}
          <div className="text-center">
            <Link href="/" className="inline-block">
              <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <span className="text-white font-bold text-2xl">EN</span>
              </div>
            </Link>
            <h2 className="text-3xl font-heading font-bold text-gray-900">
              Welcome back
            </h2>
            <p className="mt-2 text-gray-600">
              Sign in to your EduNerve account
            </p>
          </div>

          {/* Login form */}
          {apiError && (
            <ErrorAlert
              message={apiError}
              onClose={() => setApiError('')}
              className="mb-4"
            />
          )}
          
          <form className="space-y-8" onSubmit={handleSubmit}>
            <div className="space-y-6">
              <div>
              <label htmlFor="email" className="label">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                className={`input ${errors.email ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''}`}
                placeholder="Enter your email"
                value={values.email}
                onChange={handleChange}
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email}</p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="label">
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  className={`input pr-10 ${errors.password ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''}`}
                  placeholder="Enter your password"
                  value={values.password}
                  onChange={handleChange}
                />
                <button
                  type="button"
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeSlashIcon className="w-5 h-5" />
                  ) : (
                    <EyeIcon className="w-5 h-5" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password}</p>
              )}
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="rememberMe"
                  name="rememberMe"
                  type="checkbox"
                  className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  checked={values.rememberMe}
                  onChange={handleChange}
                />
                <label htmlFor="rememberMe" className="ml-2 text-sm text-gray-700">
                  Remember me
                </label>
              </div>
              <Link 
                href="/forgot-password"
                className="text-sm text-primary-600 hover:text-primary-500"
              >
                Forgot password?
              </Link>
            </div>

            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {isSubmitting ? (
                <>
                  <LoadingSpinner size="sm" color="white" className="mr-2" />
                  Signing in...
                </>
              ) : (
                'Sign in'
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">Or continue with</span>
            </div>
          </div>

          {/* Social login */}
          <div className="grid grid-cols-2 gap-3">
            <button className="btn-secondary">
              <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Google
            </button>
            <button className="btn-secondary">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
              Facebook
            </button>
          </div>

          {/* Sign up link */}
          <div className="text-center">
            <p className="text-sm text-gray-600">
              Don't have an account?{' '}
              <Link 
                href="/signup"
                className="font-medium text-primary-600 hover:text-primary-500"
              >
                Sign up for free
              </Link>
            </p>
          </div>
        </motion.div>
      </div>

      {/* Right side - Illustration/Image */}
      <div className="hidden lg:flex lg:flex-1 lg:relative">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-600 to-secondary-600"></div>
        <div className="relative flex items-center justify-center w-full p-16">
          <div className="text-center text-white max-w-md">
            <div className="text-6xl mb-6">🎓</div>
            <h3 className="text-2xl font-heading font-bold mb-4">
              Join thousands of schools across Africa
            </h3>
            <p className="text-primary-100 leading-relaxed">
              Empowering education with AI-powered tools, offline-first design, 
              and seamless communication for the modern African classroom.
            </p>
            
            {/* Stats */}
            <div className="grid grid-cols-3 gap-4 mt-8 pt-8 border-t border-primary-400">
              <div>
                <div className="text-xl font-bold">500+</div>
                <div className="text-sm text-primary-200">Schools</div>
              </div>
              <div>
                <div className="text-xl font-bold">50K+</div>
                <div className="text-sm text-primary-200">Students</div>
              </div>
              <div>
                <div className="text-xl font-bold">15</div>
                <div className="text-sm text-primary-200">Countries</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
