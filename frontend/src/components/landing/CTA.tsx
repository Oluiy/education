export default function CTA() {
  return (
    <section className="py-20 african-gradient">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="text-3xl lg:text-4xl font-heading font-bold text-white mb-6">
          Ready to Transform Your School?
        </h2>
        <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
          Join hundreds of schools already using EduNerve to deliver world-class education. 
          Start your free trial today—no credit card required.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-8">
          <a 
            href="/signup"
            className="btn-lg px-8 py-3 bg-white text-primary-600 hover:bg-gray-50 font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all duration-200"
          >
            Start Free Trial
          </a>
          <a 
            href="/demo"
            className="btn-lg px-8 py-3 bg-transparent text-white border-2 border-white hover:bg-white hover:text-primary-600 font-semibold rounded-lg transition-all duration-200"
          >
            Schedule Demo
          </a>
        </div>
        
        <div className="text-white/80 text-sm space-y-1">
          <div>✓ 14-day free trial</div>
          <div>✓ No setup fees</div>
          <div>✓ Cancel anytime</div>
        </div>
      </div>
    </section>
  )
}
