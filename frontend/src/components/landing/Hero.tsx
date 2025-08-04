'use client'

import Link from 'next/link'
import { ArrowRightIcon, PlayIcon } from '@heroicons/react/24/outline'
import { motion } from 'framer-motion'

const fadeInUp = {
  initial: { opacity: 0, y: 60 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.6 } }
}

const staggerChildren = {
  animate: {
    transition: {
      staggerChildren: 0.1
    }
  }
}

export default function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background with African pattern */}
      <div className="absolute inset-0 african-pattern opacity-5"></div>
      <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-secondary-50"></div>
      
      {/* Floating shapes */}
      <div className="absolute top-20 left-10 w-20 h-20 bg-primary-200 rounded-full opacity-20 animate-bounce-subtle"></div>
      <div className="absolute top-40 right-20 w-16 h-16 bg-secondary-200 rounded-full opacity-20 animate-bounce-subtle" style={{animationDelay: '1s'}}></div>
      <div className="absolute bottom-40 left-20 w-12 h-12 bg-primary-300 rounded-full opacity-20 animate-bounce-subtle" style={{animationDelay: '2s'}}></div>
      
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
        <motion.div 
          className="text-center"
          variants={staggerChildren}
          initial="initial"
          animate="animate"
        >
          {/* Badge */}
          <motion.div variants={fadeInUp} className="mb-8">
            <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-primary-100 text-primary-800 border border-primary-200">
              🌍 Transforming African Education
            </span>
          </motion.div>

          {/* Main heading */}
          <motion.h1 
            variants={fadeInUp}
            className="text-4xl sm:text-5xl lg:text-6xl font-heading font-bold text-gray-900 mb-6 text-balance"
          >
            AI-Powered Learning for{' '}
            <span className="bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
              African Schools
            </span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p 
            variants={fadeInUp}
            className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto text-balance leading-relaxed"
          >
            Empower secondary schools across Africa with our offline-first learning management system. 
            Features AI tutoring, smart content creation, and seamless communication—even without internet.
          </motion.p>

          {/* Key benefits */}
          <motion.div 
            variants={fadeInUp}
            className="flex flex-wrap justify-center gap-6 mb-10 text-sm text-gray-600"
          >
            <div className="flex items-center">
              <div className="w-2 h-2 bg-primary-500 rounded-full mr-2"></div>
              Offline-First Design
            </div>
            <div className="flex items-center">
              <div className="w-2 h-2 bg-secondary-500 rounded-full mr-2"></div>
              AI-Powered Tutoring
            </div>
            <div className="flex items-center">
              <div className="w-2 h-2 bg-primary-500 rounded-full mr-2"></div>
              Multi-Language Support
            </div>
            <div className="flex items-center">
              <div className="w-2 h-2 bg-secondary-500 rounded-full mr-2"></div>
              Affordable Pricing
            </div>
          </motion.div>

          {/* CTA buttons */}
          <motion.div 
            variants={fadeInUp}
            className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12"
          >
            <Link 
              href="/signup"
              className="btn-primary btn-lg group"
            >
              Start Free Trial
              <ArrowRightIcon className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform duration-200" />
            </Link>
            <button className="btn-secondary btn-lg group">
              <PlayIcon className="mr-2 w-4 h-4" />
              Watch Demo
            </button>
          </motion.div>

          {/* Trust indicators */}
          <motion.div variants={fadeInUp} className="text-center">
            <p className="text-sm text-gray-900 mb-4">Trusted by schools across Africa</p>
            <div className="flex justify-center items-center space-x-8 opacity-60">
              <div className="text-xs font-medium text-gray-900">500+ Schools</div>
              <div className="w-1 h-1 bg-gray-700 rounded-full"></div>
              <div className="text-xs font-medium text-gray-900">50,000+ Students</div>
              <div className="w-1 h-1 bg-gray-700 rounded-full"></div>
              <div className="text-xs font-medium text-gray-900">15 Countries</div>
            </div>
          </motion.div>
        </motion.div>

        {/* Hero image/illustration */}
        <motion.div 
          className="mt-16 relative"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
        >
          <div className="relative max-w-5xl mx-auto">
            {/* Dashboard mockup */}
            <div className="relative bg-white rounded-2xl shadow-strong p-1 transform perspective-1000 rotate-x-12">
              <div className="bg-gray-100 rounded-xl aspect-video flex items-center justify-center">
                <div className="text-center space-y-4">
                  <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl mx-auto flex items-center justify-center">
                    <span className="text-white font-bold text-xl">EN</span>
                  </div>
                  <div className="space-y-2">
                    <div className="h-4 bg-gray-300 rounded w-32 mx-auto"></div>
                    <div className="h-3 bg-gray-200 rounded w-24 mx-auto"></div>
                  </div>
                  <div className="grid grid-cols-3 gap-2 max-w-xs mx-auto">
                    <div className="h-16 bg-primary-100 rounded-lg"></div>
                    <div className="h-16 bg-secondary-100 rounded-lg"></div>
                    <div className="h-16 bg-primary-100 rounded-lg"></div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Floating UI elements */}
            <div className="absolute -top-4 -left-4 bg-white rounded-lg shadow-medium p-3 animate-bounce-subtle">
              <div className="text-xs text-gray-600">📚 New Assignment</div>
              <div className="text-sm font-medium">Mathematics Quiz</div>
            </div>
            
            <div className="absolute -bottom-4 -right-4 bg-white rounded-lg shadow-medium p-3 animate-bounce-subtle" style={{animationDelay: '1s'}}>
              <div className="text-xs text-gray-600">🤖 AI Tutor</div>
              <div className="text-sm font-medium">Ready to help!</div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
