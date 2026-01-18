import { useFadeIn } from '../hooks/useFadeIn'
import './Pricing.css'

function Pricing() {
  const [ref, isVisible] = useFadeIn({ threshold: 0.1 })
  const handleStartFree = () => {
    // Scroll to the top to show the input form
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <section 
      ref={ref}
      className={`pricing fade-in-section ${isVisible ? 'is-visible' : ''}`}
    >
      <div className="pricing-container">
        <h2 className="pricing-title">Pay per analysis: $0.006</h2>
        <p className="pricing-subtitle">No monthly fees. No surprises.</p>
        <button className="btn-start-free" onClick={handleStartFree}>
          Start Free
        </button>
      </div>
    </section>
  )
}

export default Pricing
