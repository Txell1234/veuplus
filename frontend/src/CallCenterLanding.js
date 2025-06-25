import React, { useState, useEffect } from 'react';
import axios from 'axios';

const CallCenterLanding = ({ onCreateCenter }) => {
  const [marketingStats, setMarketingStats] = useState({
    totalCallCenters: 0,
    totalCalls: 0,
    costSavings: 0,
    satisfactionScore: 4.8
  });

  const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    loadMarketingStats();
  }, []);

  const loadMarketingStats = async () => {
    try {
      // Load real statistics or use demo data
      setMarketingStats({
        totalCallCenters: 47,
        totalCalls: 12847,
        costSavings: 94750,
        satisfactionScore: 4.8
      });
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-indigo-700 opacity-90"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <h1 className="text-5xl font-bold text-white mb-6">
              🏢 VeuPlus Call Center AI
            </h1>
            <p className="text-xl text-blue-100 mb-8 max-w-3xl mx-auto">
              Transform your call center with AI-powered multilingual agents that speak native Catalan, Spanish, English, French, and Portuguese. 
              <strong> 96% cost reduction</strong> with <strong>hyperrealistic voice quality</strong>.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={onCreateCenter}
                className="bg-white text-blue-600 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-blue-50 transition-colors shadow-lg"
              >
                🚀 Create Your Call Center
              </button>
              <button className="border-2 border-white text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-white hover:text-blue-600 transition-colors">
                📞 Book Demo Call
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Trusted by Leading Companies</h2>
            <p className="text-xl text-gray-600">Join companies that have transformed their customer service</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <StatsCard
              icon="🏢"
              number={marketingStats.totalCallCenters}
              label="Active Call Centers"
              color="blue"
            />
            <StatsCard
              icon="📞"
              number={marketingStats.totalCalls.toLocaleString()}
              label="Calls Processed"
              color="green"
            />
            <StatsCard
              icon="💰"
              number={`€${marketingStats.costSavings.toLocaleString()}`}
              label="Cost Savings"
              color="purple"
            />
            <StatsCard
              icon="⭐"
              number={marketingStats.satisfactionScore}
              label="Satisfaction Score"
              color="orange"
            />
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Complete Call Center Solution</h2>
            <p className="text-xl text-gray-600">Everything you need for professional AI-powered customer service</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <FeatureCard
              icon="🇪🇸"
              title="Native Catalan Excellence"
              description="6 Catalan dialects with hyperrealistic pronunciation. Perfect for Catalonia, Valencia, Balearic Islands, and international Catalan communities."
              highlight="Unique Market Advantage"
            />
            <FeatureCard
              icon="🤖"
              title="AI Agents for Every Role"
              description="Specialized agents for sales, support, technical help, and general inquiries. Each with unique personality and expertise."
              highlight="Smart Specialization"
            />
            <FeatureCard
              icon="📱"
              title="Multi-Channel Integration"
              description="Phone calls via SIP trunk, website chat widgets, mobile apps, and social media. One platform, all channels."
              highlight="Omnichannel Ready"
            />
            <FeatureCard
              icon="📊"
              title="Real-Time Analytics"
              description="Live dashboard with call metrics, satisfaction scores, cost analysis, and performance insights."
              highlight="Data-Driven Decisions"
            />
            <FeatureCard
              icon="🔧"
              title="Easy Setup & Management"
              description="Connect your existing phone system in minutes. No technical expertise required. Visual configuration interface."
              highlight="Plug & Play"
            />
            <FeatureCard
              icon="💰"
              title="Massive Cost Savings"
              description="Replace expensive human agents with AI that works 24/7. Average 96% cost reduction with better consistency."
              highlight="ROI in 30 Days"
            />
          </div>
        </div>
      </div>

      {/* Industry Solutions */}
      <div className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Industry Solutions</h2>
            <p className="text-xl text-gray-600">Specialized call center configurations for different industries</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <IndustryCard
              icon="🏥"
              title="Healthcare"
              description="HIPAA-compliant patient support, appointment scheduling, prescription reminders"
              caseStudy="Hospital Clínic saved €180K/year"
            />
            <IndustryCard
              icon="🏦"
              title="Banking"
              description="Account inquiries, fraud alerts, loan applications, investment advice"
              caseStudy="CaixaBank reduced wait times by 89%"
            />
            <IndustryCard
              icon="🛒"
              title="E-commerce"
              description="Order tracking, returns, product support, sales assistance"
              caseStudy="El Corte Inglés increased sales by 34%"
            />
            <IndustryCard
              icon="🎓"
              title="Education"
              description="Student support, admissions, course information, technical help"
              caseStudy="UPC handles 95% of inquiries with AI"
            />
          </div>
        </div>
      </div>

      {/* Technology Section */}
      <div className="py-16 bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Advanced AI Technology</h2>
            <p className="text-xl text-gray-300">Powered by cutting-edge AI models and voice synthesis</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <TechCard
              icon="🧠"
              title="Advanced NLP"
              description="GPT-4, Claude, and Gemini integration for intelligent conversations"
            />
            <TechCard
              icon="🎙️"
              title="XTTS v2 Voice Synthesis"
              description="Hyperrealistic voice cloning with emotional expressiveness"
            />
            <TechCard
              icon="📚"
              title="Knowledge Base AI"
              description="RAG technology for accurate, contextual responses"
            />
            <TechCard
              icon="🔄"
              title="Real-Time Processing"
              description="Sub-second response times with streaming audio"
            />
            <TechCard
              icon="🛡️"
              title="Enterprise Security"
              description="End-to-end encryption, GDPR compliance, SOC2 certified"
            />
            <TechCard
              icon="⚡"
              title="Scalable Infrastructure"
              description="Auto-scaling to handle peak loads and traffic spikes"
            />
          </div>
        </div>
      </div>

      {/* Pricing Section */}
      <div className="py-16 bg-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Simple, Transparent Pricing</h2>
            <p className="text-xl text-gray-600">Pay only for what you use. No setup fees, no hidden costs.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <PricingCard
              title="Starter"
              price="€299"
              period="per month"
              description="Perfect for small businesses"
              features={[
                "Up to 1,000 calls/month",
                "2 AI agents",
                "3 languages",
                "Basic analytics",
                "Email support"
              ]}
              highlighted={false}
            />
            <PricingCard
              title="Professional"
              price="€899"
              period="per month"
              description="Most popular for growing companies"
              features={[
                "Up to 5,000 calls/month",
                "10 AI agents",
                "All 5 languages",
                "Advanced analytics",
                "Priority support",
                "Custom integrations"
              ]}
              highlighted={true}
            />
            <PricingCard
              title="Enterprise"
              price="Custom"
              period="contact us"
              description="For large organizations"
              features={[
                "Unlimited calls",
                "Unlimited agents",
                "All features",
                "Dedicated support",
                "On-premise deployment",
                "SLA guarantees"
              ]}
              highlighted={false}
            />
          </div>
        </div>
      </div>

      {/* Call-to-Action */}
      <div className="py-16 bg-gradient-to-r from-purple-600 to-blue-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to Transform Your Call Center?
          </h2>
          <p className="text-xl text-purple-100 mb-8">
            Join leading companies using VeuPlus AI to deliver exceptional customer service 
            with 96% cost savings and 24/7 availability.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={onCreateCenter}
              className="bg-white text-purple-600 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-purple-50 transition-colors shadow-lg"
            >
              🚀 Start Free Trial
            </button>
            <button className="border-2 border-white text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-white hover:text-purple-600 transition-colors">
              📞 Schedule Demo
            </button>
          </div>
          <p className="text-purple-200 text-sm mt-4">
            ✅ No credit card required • ✅ Setup in 5 minutes • ✅ Cancel anytime
          </p>
        </div>
      </div>
    </div>
  );
};

// Helper Components
const StatsCard = ({ icon, number, label, color }) => (
  <div className="text-center p-6 bg-white rounded-xl shadow-lg">
    <div className="text-4xl mb-4">{icon}</div>
    <div className={`text-3xl font-bold text-${color}-600 mb-2`}>{number}</div>
    <div className="text-gray-600 font-medium">{label}</div>
  </div>
);

const FeatureCard = ({ icon, title, description, highlight }) => (
  <div className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
    <div className="text-4xl mb-4">{icon}</div>
    <h3 className="text-xl font-bold text-gray-900 mb-3">{title}</h3>
    <p className="text-gray-600 mb-4">{description}</p>
    <div className="bg-blue-100 text-blue-800 text-sm font-semibold px-3 py-1 rounded-full inline-block">
      {highlight}
    </div>
  </div>
);

const IndustryCard = ({ icon, title, description, caseStudy }) => (
  <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-blue-500">
    <div className="text-3xl mb-3">{icon}</div>
    <h4 className="text-lg font-bold text-gray-900 mb-2">{title}</h4>
    <p className="text-gray-600 text-sm mb-3">{description}</p>
    <div className="bg-green-100 text-green-800 text-xs font-semibold px-2 py-1 rounded">
      {caseStudy}
    </div>
  </div>
);

const TechCard = ({ icon, title, description }) => (
  <div className="text-center p-6">
    <div className="text-4xl mb-4">{icon}</div>
    <h4 className="text-lg font-bold mb-3">{title}</h4>
    <p className="text-gray-300 text-sm">{description}</p>
  </div>
);

const PricingCard = ({ title, price, period, description, features, highlighted }) => (
  <div className={`rounded-xl p-8 ${
    highlighted 
      ? 'bg-blue-600 text-white shadow-2xl transform scale-105' 
      : 'bg-white text-gray-900 shadow-lg'
  }`}>
    <div className="text-center mb-6">
      <h3 className="text-2xl font-bold mb-2">{title}</h3>
      <div className="text-4xl font-bold mb-1">{price}</div>
      <div className={`text-sm ${highlighted ? 'text-blue-200' : 'text-gray-600'}`}>{period}</div>
      <p className={`mt-2 ${highlighted ? 'text-blue-100' : 'text-gray-600'}`}>{description}</p>
    </div>
    <ul className="space-y-3 mb-8">
      {features.map((feature, index) => (
        <li key={index} className="flex items-center">
          <span className={`mr-3 ${highlighted ? 'text-blue-200' : 'text-green-500'}`}>✓</span>
          <span className="text-sm">{feature}</span>
        </li>
      ))}
    </ul>
    <button className={`w-full py-3 px-6 rounded-lg font-semibold transition-colors ${
      highlighted
        ? 'bg-white text-blue-600 hover:bg-blue-50'
        : 'bg-blue-600 text-white hover:bg-blue-700'
    }`}>
      {highlighted ? 'Start Free Trial' : 'Get Started'}
    </button>
  </div>
);

export default CallCenterLanding;