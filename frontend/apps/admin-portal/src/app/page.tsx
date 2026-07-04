import Link from 'next/link'
import { ArrowRight, CheckCircle2, Sparkles } from 'lucide-react'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <header className="border-b bg-white/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="h-8 w-8 text-blue-600" />
            <span className="text-2xl font-bold text-gray-900">NBFC Suite</span>
          </div>
          <Link 
            href="/login"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Sign In
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
            </span>
            Version 2.0 - Fresh Implementation
          </div>

          {/* Main Heading */}
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 leading-tight">
            Tier-1 Enterprise Platform for
            <span className="text-blue-600"> Financial Institutions</span>
          </h1>

          {/* Subtitle */}
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Complete Financial Institution Operating System with 78+ modules, 
            AI-powered intelligence, and 100% RBI compliance.
          </p>

          {/* Rating */}
          <div className="flex items-center justify-center gap-2">
            <div className="flex">
              {[...Array(5)].map((_, i) => (
                <span key={i} className="text-yellow-400 text-2xl">★</span>
              ))}
            </div>
            <span className="text-gray-600 font-semibold">9.8/10 Platform Rating</span>
          </div>

          {/* CTA Buttons */}
          <div className="flex items-center justify-center gap-4 pt-4">
            <Link
              href="/dashboard"
              className="group inline-flex items-center gap-2 px-8 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold"
            >
              Get Started
              <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition" />
            </Link>
            <Link
              href="/docs"
              className="inline-flex items-center gap-2 px-8 py-4 border-2 border-gray-300 text-gray-700 rounded-lg hover:border-blue-600 hover:text-blue-600 transition font-semibold"
            >
              Documentation
            </Link>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-6 pt-16">
            <FeatureCard
              icon="🚀"
              title="No-Code Configuration"
              description="Launch products, workflows, and rules without coding"
            />
            <FeatureCard
              icon="🤖"
              title="AI-Powered Intelligence"
              description="Instant loan decisions in less than 60 seconds"
            />
            <FeatureCard
              icon="🏢"
              title="Multi-Tenant SaaS"
              description="Serve multiple organizations from single installation"
            />
            <FeatureCard
              icon="✅"
              title="RBI Compliant"
              description="100% automated regulatory reporting"
            />
            <FeatureCard
              icon="🔒"
              title="Banking-Grade Security"
              description="Advanced fraud detection and encryption"
            />
            <FeatureCard
              icon="📱"
              title="Mobile-First Design"
              description="Flutter iOS + Android applications"
            />
          </div>

          {/* Stats */}
          <div className="grid md:grid-cols-4 gap-8 pt-16 border-t">
            <Stat value="78+" label="Modules" />
            <Stat value="100%" label="RBI Compliance" />
            <Stat value="<60s" label="Loan Decisions" />
            <Stat value="9.8/10" label="Platform Rating" />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t mt-16 py-8 bg-white/50">
        <div className="container mx-auto px-4 text-center text-gray-600">
          <p>© 2026 NBFC Suite. Tier-1 Enterprise-Grade Platform.</p>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="p-6 bg-white rounded-xl border border-gray-200 hover:border-blue-300 hover:shadow-lg transition">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm">{description}</p>
    </div>
  )
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div>
      <div className="text-3xl font-bold text-blue-600">{value}</div>
      <div className="text-sm text-gray-600 mt-1">{label}</div>
    </div>
  )
}
