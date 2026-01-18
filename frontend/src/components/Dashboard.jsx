import { useState } from 'react'
import RepoInput from './RepoInput'
import AnalysisProgress from './AnalysisProgress'
import Results from './Results'
import './Dashboard.css'

function Dashboard() {
  const [repoUrl, setRepoUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [progress, setProgress] = useState([])
  const [error, setError] = useState(null)

  const handleAnalyze = async (url) => {
    setRepoUrl(url)
    setLoading(true)
    setResults(null)
    setError(null)
    setProgress([])

    try {
      const response = await fetch('http://localhost:8000/api/v1/analyze/github', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          repo_url: url,
          branch: 'main',
          use_token_company: true
        })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }))
        throw new Error(errorData.detail || `HTTP ${response.status}`)
      }

      const data = await response.json()
      setResults(data)
    } catch (err) {
      setError(err.message || 'Failed to analyze repository')
      console.error('Analysis error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setRepoUrl('')
    setResults(null)
    setError(null)
    setProgress([])
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">⚖️</span>
            <h1>Veritas.dev</h1>
          </div>
          <p className="tagline">Documentation Verification Dashboard</p>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="dashboard-container">
          {!results && !loading && (
            <RepoInput onSubmit={handleAnalyze} />
          )}

          {loading && (
            <AnalysisProgress repoUrl={repoUrl} />
          )}

          {error && (
            <div className="error-message">
              <h3>❌ Error</h3>
              <p>{error}</p>
              <button onClick={handleReset} className="btn btn-secondary">
                Try Again
              </button>
            </div>
          )}

          {results && !loading && (
            <Results 
              results={results} 
              repoUrl={repoUrl}
              onReset={handleReset}
            />
          )}
        </div>
      </main>
    </div>
  )
}

export default Dashboard