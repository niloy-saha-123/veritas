import { useState, useEffect } from 'react'
import AnalysisProgress from './AnalysisProgress'
import Results from './Results'
import Features from './Features'
import HowItWorks from './HowItWorks'
import BuiltForTeams from './BuiltForTeams'
import TrustScoreGraph from './TrustScoreGraph'
import Pricing from './Pricing'
import Footer from './Footer'
import SignIn from './SignIn'
import UserDashboard from './UserDashboard'
import './Dashboard.css'

function Dashboard() {
  const [repoUrl, setRepoUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [progress, setProgress] = useState([])
  const [error, setError] = useState(null)
  const [user, setUser] = useState(null)
  const [userToken, setUserToken] = useState(null)
  const [showUserDashboard, setShowUserDashboard] = useState(false)
  const [userRepos, setUserRepos] = useState([])
  const [showRepoSuggestions, setShowRepoSuggestions] = useState(false)
  const [filteredRepos, setFilteredRepos] = useState([])

  // Check for user in URL params on mount (from OAuth callback)
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const userId = urlParams.get('user_id')
    const username = urlParams.get('username')
    
    if (userId && username && !user) {
      setUser({ id: parseInt(userId), username })
      // Clean URL
      window.history.replaceState({}, document.title, window.location.pathname)
    }
  }, [user])

  // Load user repositories when user is signed in
  useEffect(() => {
    if (user && user.id) {
      loadUserRepos()
    } else {
      setUserRepos([])
    }
  }, [user])

  const loadUserRepos = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/dashboard/${user.id}`)
      if (response.ok) {
        const data = await response.json()
        setUserRepos(data.repositories || [])
      }
    } catch (err) {
      console.error('Failed to load user repos:', err)
    }
  }

  const handleRepoInputChange = (e) => {
    const value = e.target.value
    setRepoUrl(value)
    
    if (user && userRepos.length > 0) {
      if (value.trim()) {
        // Filter repositories based on input
        const filtered = userRepos.filter(repo => 
          repo.repo_url.toLowerCase().includes(value.toLowerCase())
        )
        setFilteredRepos(filtered)
        setShowRepoSuggestions(filtered.length > 0)
      } else {
        // Show all repositories when input is empty
        setFilteredRepos(userRepos)
        setShowRepoSuggestions(true)
      }
    } else {
      setShowRepoSuggestions(false)
    }
  }

  const handleRepoInputFocus = () => {
    if (user && userRepos.length > 0) {
      if (repoUrl.trim()) {
        // Filter based on current input
        const filtered = userRepos.filter(repo => 
          repo.repo_url.toLowerCase().includes(repoUrl.toLowerCase())
        )
        setFilteredRepos(filtered)
        setShowRepoSuggestions(filtered.length > 0)
      } else {
        // Show all repositories when input is empty
        setFilteredRepos(userRepos)
        setShowRepoSuggestions(true)
      }
    }
  }

  const handleSelectRepo = (repoUrl) => {
    setRepoUrl(repoUrl)
    setShowRepoSuggestions(false)
  }

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
          use_token_company: true,
          user_id: user?.id || null
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

  const handleSubmit = (e) => {
    e.preventDefault()
    console.log('Form submitted with URL:', repoUrl)
    if (repoUrl.trim()) {
      handleAnalyze(repoUrl.trim())
    } else {
      console.error('Empty repo URL')
    }
  }

  const handleReset = () => {
    setRepoUrl('')
    setResults(null)
    setError(null)
    setProgress([])
    setShowUserDashboard(false)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-nav">
          <div 
            className="logo clickable" 
            onClick={handleReset}
            style={{ cursor: 'pointer' }}
            title="Back to Home"
          >
            Veritas
          </div>
          <nav className="header-links">
            <a href="#how-it-works" onClick={(e) => {
              e.preventDefault()
              document.querySelector('#how-it-works')?.scrollIntoView({ behavior: 'smooth' })
            }}>How it Works</a>
            <a href="#features" onClick={(e) => {
              e.preventDefault()
              document.querySelector('#features')?.scrollIntoView({ behavior: 'smooth' })
            }}>Features</a>
          </nav>
        </div>
        <div className="header-actions">
          {user && (
            <span 
              className="user-info clickable" 
              onClick={() => setShowUserDashboard(!showUserDashboard)}
              title="View Dashboard"
            >
              👤 {user.username}
            </span>
          )}
          <SignIn 
            user={user}
            onSignIn={setUser}
            onTokenSave={(data) => {
              setUserToken(data)
              setUser({ id: data.userId, username: user?.username || 'User' })
            }}
          />
        </div>
      </header>

      {showUserDashboard && user ? (
        <UserDashboard 
          userId={user.id}
          onAnalyze={(repoUrl) => {
            setRepoUrl(repoUrl)
            setShowUserDashboard(false)
            handleAnalyze(repoUrl)
          }}
          onSignOut={() => {
            setUser(null)
            setShowUserDashboard(false)
            handleReset()
          }}
        />
      ) : (
      <main className="dashboard-main">
        {!results && !loading && !error && (
          <div className="hero-section">
            <div className="hero-content">
              <div className="hero-left">
                <h1 className="hero-headline">
                  Documentation<br />
                  that never<br />
                  lies.
                </h1>
                <p className="hero-description">
                  AI-powered verification ensures your docs match your code— automatically. No more wasted hours on outdated examples.
                </p>
                <form onSubmit={handleSubmit} className="repo-form">
                  <div className="repo-input-wrapper">
                    <input
                      type="url"
                      value={repoUrl}
                      onChange={handleRepoInputChange}
                      onFocus={handleRepoInputFocus}
                      onBlur={() => {
                        // Delay hiding suggestions to allow click
                        setTimeout(() => setShowRepoSuggestions(false), 200)
                      }}
                      placeholder="https://github.com/user/repo"
                      className="repo-input"
                      required
                    />
                    {showRepoSuggestions && filteredRepos.length > 0 && (
                      <div className="repo-suggestions">
                        {filteredRepos.map((repo) => (
                          <div
                            key={repo.id}
                            className="repo-suggestion-item"
                            onClick={() => handleSelectRepo(repo.repo_url)}
                          >
                            <span className="repo-suggestion-name">{repo.repo_url.split('/').pop()}</span>
                            <span className="repo-suggestion-url">{repo.repo_url}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  <button type="submit" className="btn-analyze">
                    Analyze Repository
                  </button>
                </form>
                <p className="hero-footer">
                  Free for open source • 5 min setup
                </p>
              </div>
              <div className="hero-right">
                <div className="code-window">
                  <div className="code-window-header">
                    <div className="window-controls">
                      <span className="control-dot red"></span>
                      <span className="control-dot yellow"></span>
                      <span className="control-dot green"></span>
                    </div>
                    <span className="code-filename">auth.py</span>
                  </div>
                  <div className="code-content">
                    <pre><code>
<span className="code-line"><span className="code-number">1</span> <span className="code-keyword">def</span> <span className="code-function">login</span>(<span className="code-param">email</span>, <span className="code-param">password</span>, <span className="code-param">mfa_token</span>):</span>
<span className="code-line"><span className="code-number">2</span> <span className="code-string">"""Authenticate user with MFA"""</span></span>
<span className="code-line"><span className="code-number">3</span> <span className="code-var">user</span> = <span className="code-function">validate_credentials</span>(<span className="code-param">email</span>, <span className="code-param">password</span>)</span>
<span className="code-line"><span className="code-number">4</span> <span className="code-keyword">return</span> <span className="code-function">verify_mfa</span>(<span className="code-var">user</span>, <span className="code-param">mfa_token</span>)</span>
                    </code></pre>
                  </div>
                </div>
                <div className="verification-status">
                  <svg className="checkmark" width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M16.667 5L7.5 14.167 3.333 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  <span>Documentation verified</span>
                </div>
              </div>
            </div>
          </div>
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
            userId={user?.id}
          />
        )}
      </main>
      )}

      {!results && !loading && !error && !showUserDashboard && (
        <>
          <HowItWorks />
          <Features />
          <BuiltForTeams />
          <TrustScoreGraph />
          <Pricing />
        </>
      )}

      <Footer />
    </div>
  )
}

export default Dashboard