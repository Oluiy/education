export default function Testimonials() {
  const testimonials = [
    {
      name: 'Dr. Amina Hassan',
      role: 'Principal, Lagos Secondary School',
      location: 'Nigeria',
      content: 'EduNerve transformed our school. Even when internet is down, our students keep learning. The AI tutor is like having extra teachers.',
      avatar: '👩🏾‍🏫'
    },
    {
      name: 'James Kiprotich',
      role: 'Mathematics Teacher',
      location: 'Kenya',
      content: 'Creating quizzes used to take hours. Now AI helps me generate quality assessments in minutes. My students love the interactive features.',
      avatar: '👨🏿‍🏫'
    },
    {
      name: 'Sarah Mukamana',
      role: 'Student, Grade 11',
      location: 'Rwanda',
      content: 'The AI tutor explains things in my local language when I\'m confused. I can study anywhere, even at home without internet.',
      avatar: '👩🏾‍🎓'
    }
  ]

  return (
    <section id="testimonials" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl lg:text-4xl font-heading font-bold text-gray-900 mb-4">
            Loved by Schools Across Africa
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            See how EduNerve is making a difference in African classrooms
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <div key={index} className="card">
              <div className="card-body">
                <div className="flex items-center mb-4">
                  <div className="text-3xl mr-3">{testimonial.avatar}</div>
                  <div>
                    <div className="font-semibold text-gray-900">{testimonial.name}</div>
                    <div className="text-sm text-gray-600">{testimonial.role}</div>
                    <div className="text-xs text-primary-600">📍 {testimonial.location}</div>
                  </div>
                </div>
                <blockquote className="text-gray-700 leading-relaxed">
                  "{testimonial.content}"
                </blockquote>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
