import './globals.css'
import type { Metadata } from 'next'
import { Inter, Lexend } from 'next/font/google'
import { Providers } from './providers'
import { Toaster } from 'react-hot-toast'

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const lexend = Lexend({ 
  subsets: ['latin'],
  variable: '--font-lexend',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'EduNerve - AI-Powered Learning for African Schools',
  description: 'Transform education in Africa with AI-powered offline-first learning management system designed for secondary schools.',
  keywords: 'education, AI, Africa, learning management system, offline, schools, students, teachers',
  authors: [{ name: 'EduNerve Team' }],
  creator: 'EduNerve',
  publisher: 'EduNerve',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL('https://edunerve.com'),
  alternates: {
    canonical: '/',
    languages: {
      'en-US': '/en-US',
      'fr-FR': '/fr-FR',
      'sw-KE': '/sw-KE',
    },
  },
  openGraph: {
    title: 'EduNerve - AI-Powered Learning for African Schools',
    description: 'Transform education in Africa with AI-powered offline-first learning management system.',
    url: 'https://edunerve.com',
    siteName: 'EduNerve',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'EduNerve - AI-Powered Learning Platform',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'EduNerve - AI-Powered Learning for African Schools',
    description: 'Transform education in Africa with AI-powered offline-first learning management system.',
    creator: '@edunerve',
    images: ['/twitter-image.jpg'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'google-site-verification-code',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} ${lexend.variable}`}>
      <body className="min-h-screen bg-gray-50 antialiased">
        <Providers>
          {children}
        </Providers>
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#22c55e',
                secondary: '#fff',
              },
            },
            error: {
              duration: 5000,
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />
      </body>
    </html>
  )
}
