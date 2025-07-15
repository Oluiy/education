export default function Stats() {
  const stats = [
    { label: 'Active Schools', value: '500+', description: 'Across 15 African countries' },
    { label: 'Students Served', value: '50K+', description: 'Learning every day' },
    { label: 'Course Completion', value: '95%', description: 'Average completion rate' },
    { label: 'Offline Capability', value: '100%', description: 'Full functionality offline' }
  ]

  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-heading font-bold text-gray-900 mb-4">
            Empowering Education Across Africa
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Join thousands of schools already transforming education with EduNerve
          </p>
        </div>
        
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-3xl lg:text-4xl font-bold text-primary-600 mb-2">
                {stat.value}
              </div>
              <div className="text-lg font-medium text-gray-900 mb-1">
                {stat.label}
              </div>
              <div className="text-sm text-gray-600">
                {stat.description}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
