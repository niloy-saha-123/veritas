import { useFadeIn } from '../hooks/useFadeIn'
import './HowItWorks.css'

function HowItWorks() {
  const [ref, isVisible] = useFadeIn({ threshold: 0.1 })
  const steps = [
    {
      id: 1,
      title: 'GitHub Webhook',
      icon: '⚡',
      description: 'Triggered automatically when code or documentation changes'
    },
    {
      id: 2,
      title: 'Fetch Code',
      icon: '📁',
      description: 'Extract all function signatures from your codebase'
    },
    {
      id: 3,
      title: 'Fetch Docs',
      icon: '📄',
      description: 'Parse documentation files and extract function references'
    },
    {
      id: 4,
      title: 'Token Compression',
      icon: '🗜️',
      description: 'Compress prompts using Bear-1 to optimize AI processing'
    },
    {
      id: 5,
      title: 'AI Analysis',
      icon: '🧠',
      description: 'Compare code and docs using Claude with semantic matching'
    },
    {
      id: 6,
      title: 'Trust Score',
      icon: '📊',
      description: 'Calculate overall documentation trust score'
    },
    {
      id: 7,
      title: 'Issue Creation',
      icon: '💬',
      description: 'Automatically create issues with discrepancies found'
    }
  ]

  return (
    <section 
      ref={ref}
      className={`how-it-works fade-in-section ${isVisible ? 'is-visible' : ''}`} 
      id="how-it-works"
    >
      <div className="how-it-works-container">
        <div className="how-it-works-header">
          <h2 className="section-subtitle">HOW IT WORKS</h2>
          <h3 className="section-title">Automatic Verification Pipeline</h3>
        </div>

        <div className="workflow-grid">
          {steps.map((step, index) => (
            <div key={step.id} className="workflow-card">
              <div className="card-number">{step.id}</div>
              <div className="card-icon">{step.icon}</div>
              <h4 className="card-title">{step.title}</h4>
              <p className="card-description">{step.description}</p>
              {index < steps.length - 1 && (
                <div className="card-arrow">→</div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default HowItWorks
