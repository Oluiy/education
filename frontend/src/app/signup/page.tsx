'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { EyeIcon, EyeSlashIcon, CheckIcon } from '@heroicons/react/24/outline'
import { useAuth } from '@/contexts/AuthContext'
import { LoadingSpinner } from '@/components/ui/Loading'
import { ErrorAlert } from '@/components/ui/Error'

export default function SignupPage() {
  const router = useRouter()
  const { signup } = useAuth()
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [currentStep, setCurrentStep] = useState(1)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [apiError, setApiError] = useState('')
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [formData, setFormData] = useState({
    // Step 1: Account type
    accountType: 'school',
    
    // Step 2: Basic info
    schoolName: '',
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    
    // Step 3: School details
    country: '',
    state: '',
    city: '',
    schoolType: 'secondary',
    studentCount: '',
    
    // Step 4: Account setup
    password: '',
    confirmPassword: '',
    agreeToTerms: false,
    subscribeNewsletter: true
  })

  const validateCurrentStep = (): boolean => {
    const errors: Record<string, string> = {}
    
    switch (currentStep) {
      case 1:
        if (!formData.accountType) {
          errors.accountType = 'Please select an account type'
        }
        break
        
      case 2:
        if (formData.accountType === 'school' && !formData.schoolName.trim()) {
          errors.schoolName = 'School name is required'
        }
        if (!formData.firstName.trim()) {
          errors.firstName = 'First name is required'
        }
        if (!formData.lastName.trim()) {
          errors.lastName = 'Last name is required'
        }
        if (!formData.email.trim()) {
          errors.email = 'Email is required'
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
          errors.email = 'Please enter a valid email address'
        }
        if (!formData.phone.trim()) {
          errors.phone = 'Phone number is required'
        }
        break
        
      case 3:
        if (!formData.country) {
          errors.country = 'Country is required'
        }
        if (!formData.state.trim()) {
          errors.state = 'State/Region is required'
        }
        if (!formData.city.trim()) {
          errors.city = 'City is required'
        }
        if (formData.accountType === 'school') {
          if (!formData.schoolType) {
            errors.schoolType = 'School type is required'
          }
          if (!formData.studentCount) {
            errors.studentCount = 'Student count is required'
          }
        }
        break
        
      case 4:
        if (!formData.password) {
          errors.password = 'Password is required'
        } else if (formData.password.length < 8) {
          errors.password = 'Password must be at least 8 characters long'
        }
        if (!formData.confirmPassword) {
          errors.confirmPassword = 'Please confirm your password'
        } else if (formData.password !== formData.confirmPassword) {
          errors.confirmPassword = 'Passwords do not match'
        }
        if (!formData.agreeToTerms) {
          errors.agreeToTerms = 'You must agree to the terms and conditions'
        }
        break
    }
    
    setFieldErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateCurrentStep()) {
      return
    }
    
    if (currentStep < 4) {
      setCurrentStep(currentStep + 1)
    } else {
      // Final submission
      setIsSubmitting(true)
      setApiError('')
      
      try {
        await signup(formData)
        // Redirect to appropriate dashboard based on account type
        switch (formData.accountType) {
          case 'teacher':
            router.push('/teacher/dashboard')
            break
          case 'parent':
            router.push('/parent/dashboard')
            break
          case 'school':
          default:
            router.push('/admin/dashboard')
        }
      } catch (error: any) {
        console.error('Signup error:', error)
        setApiError(error.message || 'Signup failed. Please try again.')
      } finally {
        setIsSubmitting(false)
      }
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target
    const checked = type === 'checkbox' ? (e.target as HTMLInputElement).checked : undefined
    
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))

    // Clear field error when user starts typing
    if (fieldErrors[name]) {
      setFieldErrors(prev => ({
        ...prev,
        [name]: ''
      }))
    }
  }

  const renderStep1 = () => (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-6"
    >
      <div className="text-center mb-8">
        <h3 className="text-xl font-heading font-semibold text-gray-900 mb-2">
          Choose your account type
        </h3>
        <p className="text-gray-600">
          Select the option that best describes you
        </p>
      </div>

      <div className="space-y-4">
        {[
          {
            value: 'school',
            title: 'School Administrator',
            description: 'Set up EduNerve for your school',
            icon: '🏫'
          },
          {
            value: 'teacher',
            title: 'Teacher',
            description: 'Join an existing school account',
            icon: '👨‍🏫'
          },
          {
            value: 'parent',
            title: 'Parent',
            description: 'Monitor your child\'s progress',
            icon: '👨‍👩‍👧‍👦'
          }
        ].map((option) => (
          <label
            key={option.value}
            className={`block p-4 border-2 rounded-lg cursor-pointer transition-all duration-200 ${
              formData.accountType === option.value
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <input
              type="radio"
              name="accountType"
              value={option.value}
              checked={formData.accountType === option.value}
              onChange={handleChange}
              className="sr-only"
            />
            <div className="flex items-center space-x-3">
              <span className="text-2xl">{option.icon}</span>
              <div className="flex-1">
                <div className="font-medium text-gray-900">{option.title}</div>
                <div className="text-sm text-gray-600">{option.description}</div>
              </div>
              {formData.accountType === option.value && (
                <CheckIcon className="w-5 h-5 text-primary-600" />
              )}
            </div>
          </label>
        ))}
      </div>
    </motion.div>
  )

  const renderStep2 = () => (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-6"
    >
      <div className="text-center mb-8">
        <h3 className="text-xl font-heading font-semibold text-gray-900 mb-2">
          Basic Information
        </h3>
        <p className="text-gray-600">
          Tell us about yourself
        </p>
      </div>

      {formData.accountType === 'school' && (
        <div>
          <label htmlFor="schoolName" className="label">
            School Name *
          </label>
          <input
            id="schoolName"
            name="schoolName"
            type="text"
            required
            className={`input ${fieldErrors.schoolName ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''}`}
            placeholder="Enter your school name"
            value={formData.schoolName}
            onChange={handleChange}
          />
          {fieldErrors.schoolName && (
            <p className="mt-1 text-sm text-red-600">{fieldErrors.schoolName}</p>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label htmlFor="firstName" className="label">
            First Name *
          </label>
          <input
            id="firstName"
            name="firstName"
            type="text"
            required
            className={`input ${fieldErrors.firstName ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''}`}
            placeholder="First name"
            value={formData.firstName}
            onChange={handleChange}
          />
          {fieldErrors.firstName && (
            <p className="mt-1 text-sm text-red-600">{fieldErrors.firstName}</p>
          )}
        </div>
        <div>
          <label htmlFor="lastName" className="label">
            Last Name *
          </label>
          <input
            id="lastName"
            name="lastName"
            type="text"
            required
            className={`input ${fieldErrors.lastName ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''}`}
            placeholder="Last name"
            value={formData.lastName}
            onChange={handleChange}
          />
          {fieldErrors.lastName && (
            <p className="mt-1 text-sm text-red-600">{fieldErrors.lastName}</p>
          )}
        </div>
      </div>

      <div>
        <label htmlFor="email" className="label">
          Email Address *
        </label>
        <input
          id="email"
          name="email"
          type="email"
          required
          className={`input ${fieldErrors.email ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''}`}
          placeholder="Enter your email"
          value={formData.email}
          onChange={handleChange}
        />
        {fieldErrors.email && (
          <p className="mt-1 text-sm text-red-600">{fieldErrors.email}</p>
        )}
      </div>

      <div>
        <label htmlFor="phone" className="label">
          Phone Number *
        </label>
        <input
          id="phone"
          name="phone"
          type="tel"
          required
          className={`input ${fieldErrors.phone ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''}`}
          placeholder="+234 xxx xxx xxxx"
          value={formData.phone}
          onChange={handleChange}
        />
        {fieldErrors.phone && (
          <p className="mt-1 text-sm text-red-600">{fieldErrors.phone}</p>
        )}
      </div>
    </motion.div>
  )

  const renderStep3 = () => (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-6"
    >
      <div className="text-center mb-8">
        <h3 className="text-xl font-heading font-semibold text-gray-900 mb-2">
          {formData.accountType === 'school' ? 'School Details' : 'Location'}
        </h3>
        <p className="text-gray-600">
          Help us customize your experience
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label htmlFor="country" className="label">
            Country *
          </label>
          <select
            id="country"
            name="country"
            required
            className="input"
            value={formData.country}
            onChange={handleChange}
          >
            <option value="">Select country</option>
            <option value="nigeria">Nigeria</option>
            <option value="kenya">Kenya</option>
            <option value="ghana">Ghana</option>
            <option value="south-africa">South Africa</option>
            <option value="uganda">Uganda</option>
            <option value="other">Other</option>
          </select>
        </div>
        <div>
          <label htmlFor="state" className="label">
            State/Region *
          </label>
          <input
            id="state"
            name="state"
            type="text"
            required
            className="input"
            placeholder="State or region"
            value={formData.state}
            onChange={handleChange}
          />
        </div>
        <div>
          <label htmlFor="city" className="label">
            City *
          </label>
          <input
            id="city"
            name="city"
            type="text"
            required
            className="input"
            placeholder="City"
            value={formData.city}
            onChange={handleChange}
          />
        </div>
      </div>

      {formData.accountType === 'school' && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label htmlFor="schoolType" className="label">
                School Type *
              </label>
              <select
                id="schoolType"
                name="schoolType"
                required
                className="input"
                value={formData.schoolType}
                onChange={handleChange}
              >
                <option value="primary">Primary School</option>
                <option value="secondary">Secondary School</option>
                <option value="mixed">Primary & Secondary</option>
                <option value="technical">Technical College</option>
              </select>
            </div>
            <div>
              <label htmlFor="studentCount" className="label">
                Number of Students *
              </label>
              <select
                id="studentCount"
                name="studentCount"
                required
                className="input"
                value={formData.studentCount}
                onChange={handleChange}
              >
                <option value="">Select range</option>
                <option value="1-50">1-50 students</option>
                <option value="51-200">51-200 students</option>
                <option value="201-500">201-500 students</option>
                <option value="501-1000">501-1000 students</option>
                <option value="1000+">1000+ students</option>
              </select>
            </div>
          </div>
        </>
      )}
    </motion.div>
  )

  const renderStep4 = () => (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-6"
    >
      <div className="text-center mb-8">
        <h3 className="text-xl font-heading font-semibold text-gray-900 mb-2">
          Secure Your Account
        </h3>
        <p className="text-gray-600">
          Create a strong password
        </p>
      </div>

      <div>
        <label htmlFor="password" className="label">
          Password *
        </label>
        <div className="relative">
          <input
            id="password"
            name="password"
            type={showPassword ? 'text' : 'password'}
            required
            className="input pr-10"
            placeholder="Create a password"
            value={formData.password}
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
      </div>

      <div>
        <label htmlFor="confirmPassword" className="label">
          Confirm Password *
        </label>
        <div className="relative">
          <input
            id="confirmPassword"
            name="confirmPassword"
            type={showConfirmPassword ? 'text' : 'password'}
            required
            className="input pr-10"
            placeholder="Confirm your password"
            value={formData.confirmPassword}
            onChange={handleChange}
          />
          <button
            type="button"
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
          >
            {showConfirmPassword ? (
              <EyeSlashIcon className="w-5 h-5" />
            ) : (
              <EyeIcon className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>

      <div className="space-y-4">
        <div className="flex items-start space-x-3">
          <input
            id="agreeToTerms"
            name="agreeToTerms"
            type="checkbox"
            required
            className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500 mt-1"
            checked={formData.agreeToTerms}
            onChange={handleChange}
          />
          <label htmlFor="agreeToTerms" className="text-sm text-gray-700">
            I agree to the{' '}
            <Link href="/terms" className="text-primary-600 hover:text-primary-500">
              Terms of Service
            </Link>{' '}
            and{' '}
            <Link href="/privacy" className="text-primary-600 hover:text-primary-500">
              Privacy Policy
            </Link>
          </label>
        </div>

        <div className="flex items-start space-x-3">
          <input
            id="subscribeNewsletter"
            name="subscribeNewsletter"
            type="checkbox"
            className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500 mt-1"
            checked={formData.subscribeNewsletter}
            onChange={handleChange}
          />
          <label htmlFor="subscribeNewsletter" className="text-sm text-gray-700">
            Subscribe to our newsletter for updates and educational tips
          </label>
        </div>
      </div>
    </motion.div>
  )

  const steps = [
    { number: 1, title: 'Account Type' },
    { number: 2, title: 'Basic Info' },
    { number: 3, title: 'Details' },
    { number: 4, title: 'Security' }
  ]

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4 sm:px-6 lg:px-8">
      <motion.div 
        className="w-full max-w-2xl"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* Header */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-block">
            <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <span className="text-white font-bold text-2xl">EN</span>
            </div>
          </Link>
          <h2 className="text-3xl font-heading font-bold text-gray-900">
            Create your account
          </h2>
          <p className="mt-2 text-gray-600">
            Join the future of African education
          </p>
        </div>

        {/* Progress steps */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            {steps.map((step, index) => (
              <div key={step.number} className="flex items-center">
                <div className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
                  currentStep >= step.number
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-200 text-gray-600'
                }`}>
                  {step.number}
                </div>
                <div className="ml-2 text-sm font-medium text-gray-700 hidden sm:block">
                  {step.title}
                </div>
                {index < steps.length - 1 && (
                  <div className={`w-8 sm:w-16 h-0.5 mx-2 sm:mx-4 ${
                    currentStep > step.number ? 'bg-primary-600' : 'bg-gray-200'
                  }`} />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Form */}
        <div className="bg-white rounded-2xl shadow-soft p-8">
          {apiError && (
            <ErrorAlert
              message={apiError}
              onClose={() => setApiError('')}
              className="mb-6"
            />
          )}
          
          <form onSubmit={handleSubmit}>
            {currentStep === 1 && renderStep1()}
            {currentStep === 2 && renderStep2()}
            {currentStep === 3 && renderStep3()}
            {currentStep === 4 && renderStep4()}

            {/* Navigation buttons */}
            <div className="flex justify-between items-center mt-8 pt-6 border-t border-gray-200">
              {currentStep > 1 ? (
                <button
                  type="button"
                  onClick={() => setCurrentStep(currentStep - 1)}
                  className="btn-secondary"
                >
                  Back
                </button>
              ) : (
                <Link href="/login" className="btn-secondary">
                  Sign in instead
                </Link>
              )}

              <button
                type="submit"
                disabled={isSubmitting}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {isSubmitting ? (
                  <>
                    <LoadingSpinner size="sm" color="white" className="mr-2" />
                    {currentStep === 4 ? 'Creating Account...' : 'Next'}
                  </>
                ) : (
                  currentStep === 4 ? 'Create Account' : 'Next'
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Additional info */}
        <div className="text-center mt-6">
          <p className="text-sm text-gray-600">
            Already have an account?{' '}
            <Link 
              href="/login"
              className="font-medium text-primary-600 hover:text-primary-500"
            >
              Sign in here
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  )
}
