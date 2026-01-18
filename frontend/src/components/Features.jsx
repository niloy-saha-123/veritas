import { useEffect, useState } from 'react'
import { useFadeIn } from '../hooks/useFadeIn'
import './Features.css'

function Features() {
  const [count, setCount] = useState(0)
  const [hasAnimated, setHasAnimated] = useState(false)
  const [fadeRef, isVisible] = useFadeIn({ threshold: 0.1 })

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !hasAnimated) {
            setHasAnimated(true)
            animateCount()
          }
        })
      },
      { threshold: 0.3 }
    )

    if (fadeRef.current) {
      observer.observe(fadeRef.current)
    }

    return () => {
      if (fadeRef.current) {
        observer.unobserve(fadeRef.current)
      }
    }
  }, [hasAnimated, fadeRef])

  const animateCount = () => {
    const target = 85
    const duration = 2000 // 2 seconds
    const steps = 60
    const increment = target / steps
    const stepDuration = duration / steps

    let current = 0
    const timer = setInterval(() => {
      current += increment
      if (current >= target) {
        setCount(target)
        clearInterval(timer)
      } else {
        setCount(Math.floor(current))
      }
    }, stepDuration)
  }

  return (
    <section 
      className={`features fade-in-section ${isVisible ? 'is-visible' : ''}`} 
      id="features" 
      ref={fadeRef}
    >
      <div className="features-container">
        <div className="features-content">
          <div className="features-left">
            <h2 className="features-title">Automatic documentation verification</h2>
            <p className="features-description">
              Veritas monitors every pull request and compares code changes against your documentation. 
              When mismatches are detected, we automatically create fix PRs with corrected docs. 
              No manual reviews. No context switching. Just accurate documentation that stays in sync with your codebase.
            </p>
          </div>
          <div className="features-right">
            <div className="stat-number">${count}B</div>
            <p className="stat-description">lost annually to broken documentation</p>
          </div>
        </div>
      </div>
    </section>
  )
}

export default Features
