import { useState } from 'react'
import './Results.css'

function Results({ results, repoUrl, onReset }) {
  const metadata = results.metadata || {}
  const discrepancies = results.discrepancies || []
  const trustScore = metadata.trust_score || 0
  const totalFunctions = metadata.total_functions || 0
  const verified = metadata.verified || 0
  
  const [creatingPR, setCreatingPR] = useState(false)
  const [prResult, setPrResult] = useState(null)

  const getScoreColor = (score) => {
    if (score >= 80) return '#22c55e' // green
    if (score >= 60) return '#eab308' // yellow
    return '#ef4444' // red
  }

  const getScoreLabel = (score) => {
    if (score >= 80) return 'Excellent'
    if (score >= 60) return 'Good'
    if (score >= 40) return 'Needs Improvement'
    return 'Poor'
  }

  const handleCreatePR = async () => {
    setCreatingPR(true)
    setPrResult(null)
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/analyze/github/create-pr', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          repo_url: repoUrl,
          branch: metadata.branch || 'main',
          discrepancies: discrepancies,
          metadata: metadata
        })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }))
        throw new Error(errorData.detail || `HTTP ${response.status}: Failed to create PR`)
      }

      const data = await response.json()
      setPrResult(data)
    } catch (err) {
      setPrResult({ 
        success: false, 
        error: err.message || 'Failed to create PR' 
      })
      console.error('PR creation error:', err)
    } finally {
      setCreatingPR(false)
    }
  }

  return (
    <div className="results-container">
      <div className="results-header">
        <div className="results-title">
          <h2>Analysis Results</h2>
          <p className="repo-url-small">{repoUrl}</p>
        </div>
        <button onClick={onReset} className="btn btn-secondary btn-small">
          New Analysis
        </button>
      </div>

      <div className="results-content">
        {/* Trust Score Card */}
        <div className="score-card">
          <div className="score-display">
            <div className="score-circle" style={{ borderColor: getScoreColor(trustScore) }}>
              <span className="score-value" style={{ color: getScoreColor(trustScore) }}>
                {trustScore}%
              </span>
            </div>
            <div className="score-info">
              <h3>Trust Score</h3>
              <p className="score-label" style={{ color: getScoreColor(trustScore) }}>
                {getScoreLabel(trustScore)}
              </p>
            </div>
          </div>

          <div className="stats-grid">
            <div className="stat-item">
              <div className="stat-value">{totalFunctions}</div>
              <div className="stat-label">Total Functions</div>
            </div>
            <div className="stat-item">
              <div className="stat-value" style={{ color: '#22c55e' }}>{verified}</div>
              <div className="stat-label">Verified</div>
            </div>
            <div className="stat-item">
              <div className="stat-value" style={{ color: '#ef4444' }}>
                {totalFunctions - verified}
              </div>
              <div className="stat-label">Issues Found</div>
            </div>
          </div>
        </div>

        {/* Discrepancies List */}
        {discrepancies.length > 0 && (
          <div className="discrepancies-card">
            <h3>Discrepancies ({discrepancies.length})</h3>
            <div className="discrepancies-list">
              {discrepancies.map((disc, index) => (
                <div key={index} className={`discrepancy-item severity-${disc.severity}`}>
                  <div className="discrepancy-header">
                    <span className={`severity-badge severity-${disc.severity}`}>
                      {disc.severity?.toUpperCase() || 'UNKNOWN'}
                    </span>
                    <span className="discrepancy-type">{disc.type?.replace('_', ' ') || 'Issue'}</span>
                  </div>
                  <div className="discrepancy-content">
                    <p className="discrepancy-description">{disc.description}</p>
                    {disc.location && (
                      <p className="discrepancy-location">📍 {disc.location}</p>
                    )}
                    {disc.suggestion && (
                      <div className="discrepancy-suggestion">
                        <strong>💡 Suggestion:</strong> {disc.suggestion}
                      </div>
                    )}
                    {(disc.code_snippet || disc.doc_snippet) && (
                      <div className="discrepancy-snippets">
                        {disc.code_snippet && (
                          <div className="snippet code-snippet">
                            <strong>Code:</strong>
                            <pre>{disc.code_snippet}</pre>
                          </div>
                        )}
                        {disc.doc_snippet && (
                          <div className="snippet doc-snippet">
                            <strong>Docs:</strong>
                            <pre>{disc.doc_snippet}</pre>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {discrepancies.length === 0 && (
          <div className="success-message">
            <div className="success-icon">✨</div>
            <h3>Perfect Match!</h3>
            <p>No discrepancies found. Your documentation perfectly matches your code.</p>
          </div>
        )}

        {/* PR Creation Section */}
        {discrepancies.length > 0 && (
          <div className="pr-section">
            <div className="pr-card">
              <h3>🚀 Create Pull Request</h3>
              <p className="pr-description">
                Automatically create a PR with documentation fixes for the {discrepancies.length} issue{discrepancies.length !== 1 ? 's' : ''} found.
              </p>
              
              <button 
                onClick={handleCreatePR} 
                className="btn btn-primary btn-large"
                disabled={creatingPR}
              >
                {creatingPR ? (
                  <>
                    <span className="spinner-small"></span>
                    Creating PR...
                  </>
                ) : (
                  '🚀 Create PR with Fixes'
                )}
              </button>
              
              {prResult && (
                prResult.success ? (
                  <div className="pr-success">
                    <div className="pr-success-header">
                      <span className="pr-success-icon">✅</span>
                      <h4>PR Created Successfully!</h4>
                    </div>
                    <div className="pr-success-content">
                      <p className="pr-url-label">Pull Request URL:</p>
                      <a 
                        href={prResult.pr_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="pr-url-link"
                      >
                        {prResult.pr_url}
                      </a>
                      {prResult.branch_name && (
                        <p className="pr-branch-info">
                          Branch: <code>{prResult.branch_name}</code>
                        </p>
                      )}
                      {prResult.files_changed > 0 && (
                        <p className="pr-files-info">
                          {prResult.files_changed} file{prResult.files_changed !== 1 ? 's' : ''} changed
                        </p>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="pr-error">
                    <div className="pr-error-header">
                      <span className="pr-error-icon">❌</span>
                      <h4>Failed to Create PR</h4>
                    </div>
                    <p className="pr-error-message">{prResult.error || 'An error occurred while creating the PR'}</p>
                    <button 
                      onClick={handleCreatePR} 
                      className="btn btn-secondary btn-small"
                      style={{ marginTop: '1rem' }}
                    >
                      Try Again
                    </button>
                  </div>
                )
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Results