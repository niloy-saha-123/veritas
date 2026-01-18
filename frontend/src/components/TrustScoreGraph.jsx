import { useFadeIn } from '../hooks/useFadeIn'
import './TrustScoreGraph.css'

function TrustScoreGraph() {
  const [ref, isVisible] = useFadeIn({ threshold: 0.1 })
  // Data points for the graph (Week 1 to Week 4)
  const dataPoints = [
    { week: 'Week 1', score: 65 },
    { week: 'Week 2', score: 75 },
    { week: 'Week 3', score: 85 },
    { week: 'Week 4', score: 92 }
  ]

  // Calculate positions for SVG (normalized to 0-100 scale, then scaled to SVG dimensions)
  const svgWidth = 400
  const svgHeight = 200
  const padding = 40
  const chartWidth = svgWidth - (padding * 2)
  const chartHeight = svgHeight - (padding * 2)
  
  // Find min/max scores for scaling
  const minScore = Math.min(...dataPoints.map(d => d.score))
  const maxScore = Math.max(...dataPoints.map(d => d.score))
  const scoreRange = maxScore - minScore || 1

  // Convert data points to SVG coordinates
  const points = dataPoints.map((point, index) => {
    const x = padding + (index / (dataPoints.length - 1)) * chartWidth
    const y = padding + chartHeight - ((point.score - minScore) / scoreRange) * chartHeight
    return { x, y, ...point }
  })

  // Create path for the line
  const pathData = points.map((point, index) => {
    return `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`
  }).join(' ')

  return (
    <section 
      ref={ref}
      className={`trust-score-graph fade-in-section ${isVisible ? 'is-visible' : ''}`}
    >
      <div className="graph-container">
        <div className="graph-card">
          <h3 className="graph-title">Trust Score Over Time</h3>
          <div className="graph-content">
            <svg 
              className="trust-score-chart" 
              viewBox={`0 0 ${svgWidth} ${svgHeight}`}
              preserveAspectRatio="xMidYMid meet"
            >
              {/* Grid lines (optional, for better readability) */}
              <defs>
                <pattern id="grid" width="80" height="40" patternUnits="userSpaceOnUse">
                  <path d="M 80 0 L 0 0 0 40" fill="none" stroke="#f0f0f0" strokeWidth="1"/>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />

              {/* Line connecting data points */}
              <path
                d={pathData}
                fill="none"
                stroke="#1a1a1a"
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
              />

              {/* Data points */}
              {points.map((point, index) => (
                <g key={index}>
                  {/* Outer circle (outline) */}
                  {index % 2 === 0 && (
                    <circle
                      cx={point.x}
                      cy={point.y}
                      r="6"
                      fill="none"
                      stroke="#e5e5e5"
                      strokeWidth="3"
                    />
                  )}
                  {/* Inner circle (solid) */}
                  <circle
                    cx={point.x}
                    cy={point.y}
                    r="4"
                    fill="#1a1a1a"
                  />
                </g>
              ))}

              {/* X-axis labels */}
              {points.map((point, index) => (
                <text
                  key={`label-${index}`}
                  x={point.x}
                  y={svgHeight - padding + 20}
                  textAnchor="middle"
                  fontSize="12"
                  fill="#666"
                  fontFamily="inherit"
                >
                  {point.week}
                </text>
              ))}
            </svg>
          </div>
        </div>
      </div>
    </section>
  )
}

export default TrustScoreGraph
