export default function Features() {
  const features = [
    {
      title: 'Offline-First Learning',
      description: 'Full functionality even without internet connection. Sync when online.',
      icon: '🌐',
      benefits: ['Works anywhere', 'Auto-sync', 'No interruptions']
    },
    {
      title: 'AI-Powered Tutoring',
      description: 'Personalized AI assistant helps students learn at their own pace.',
      icon: '🤖',
      benefits: ['24/7 support', 'Adaptive learning', 'Instant feedback']
    },
    {
      title: 'Smart Content Creation',
      description: 'AI helps teachers create quizzes, assignments, and study materials.',
      icon: '📚',
      benefits: ['Auto-generation', 'Multi-format', 'Quality assured']
    },
    {
      title: 'Multi-Language Support',
      description: 'Available in major African languages with AI translation.',
      icon: '🌍',
      benefits: ['Local languages', 'Auto-translate', 'Cultural context']
    },
    {
      title: 'Real-time Analytics',
      description: 'Track student progress and identify areas for improvement.',
      icon: '📊',
      benefits: ['Performance insights', 'Progress tracking', 'Predictive analytics']
    },
    {
      title: 'Seamless Communication',
      description: 'Connect teachers, students, and parents with integrated messaging.',
      icon: '💬',
      benefits: ['Multi-channel', 'Instant notifications', 'Group communication']
    }
  ]

  return (
    <section id="features" className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl lg:text-4xl font-heading font-bold text-gray-900 mb-4">
            Everything You Need for Modern Education
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Our comprehensive platform combines the latest in AI technology with practical solutions 
            designed specifically for African educational environments.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="card group hover:shadow-medium transition-all duration-300">
              <div className="card-body">
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-heading font-semibold text-gray-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600 mb-4 leading-relaxed">
                  {feature.description}
                </p>
                <ul className="space-y-2">
                  {feature.benefits.map((benefit, i) => (
                    <li key={i} className="flex items-center text-sm text-gray-600">
                      <div className="w-1.5 h-1.5 bg-primary-500 rounded-full mr-3"></div>
                      {benefit}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
