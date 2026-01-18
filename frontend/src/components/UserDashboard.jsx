import { useState, useEffect } from 'react'
import Results from './Results'
import './UserDashboard.css'

function UserDashboard({ userId, onAnalyze, onSignOut }) {
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [deletingId, setDeletingId] = useState(null)
  const [showAddRepoForm, setShowAddRepoForm] = useState(false)
  const [newRepoToken, setNewRepoToken] = useState('')
  const [newRepoUrl, setNewRepoUrl] = useState('')
  const [addingRepo, setAddingRepo] = useState(false)
  const [selectedHistory, setSelectedHistory] = useState(null)
  const [deletingRepoId, setDeletingRepoId] = useState(null)

  useEffect(() => {
    if (userId) {
      loadDashboard()
    }
  }, [userId])

  const loadDashboard = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`http://localhost:8000/api/v1/dashboard/${userId}`)
      if (!response.ok) {
        throw new Error('Failed to load dashboard')
      }
      const data = await response.json()
      setDashboardData(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteHistory = async (historyId) => {
    if (!confirm('Are you sure you want to delete this analysis history entry?')) {
      return
    }

    setDeletingId(historyId)
    try {
      const response = await fetch(`http://localhost:8000/api/v1/dashboard/analysis/history/${historyId}?user_id=${userId}`, {
        method: 'DELETE'
      })

      if (!response.ok) {
        throw new Error('Failed to delete history entry')
      }

      // Reload dashboard to reflect changes
      await loadDashboard()
    } catch (err) {
      alert(`Failed to delete: ${err.message}`)
    } finally {
      setDeletingId(null)
    }
  }

  const handleDeleteRepository = async (repoId, repoUrl) => {
    if (!confirm(`Are you sure you want to remove the repository "${repoUrl}"? This will also remove all associated analysis history.`)) {
      return
    }

    setDeletingRepoId(repoId)
    try {
      const response = await fetch(`http://localhost:8000/api/v1/dashboard/repository/${repoId}?user_id=${userId}`, {
        method: 'DELETE'
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to delete repository')
      }

      // Reload dashboard to reflect changes
      await loadDashboard()
    } catch (err) {
      alert(`Failed to delete repository: ${err.message}`)
    } finally {
      setDeletingRepoId(null)
    }
  }

  const handleAddRepository = async (e) => {
    e.preventDefault()
    setAddingRepo(true)
    setError(null)

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/save-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: newRepoToken.trim(),
          repo_url: newRepoUrl.trim(),
          user_id: userId
        })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }))
        throw new Error(errorData.detail || 'Failed to add repository')
      }

      // Reload dashboard to show new repository
      await loadDashboard()
      setShowAddRepoForm(false)
      setNewRepoToken('')
      setNewRepoUrl('')
    } catch (err) {
      setError(err.message || 'Failed to add repository')
    } finally {
      setAddingRepo(false)
    }
  }

  const handleAnalyzeRepo = (repoUrl) => {
    if (onAnalyze) {
      onAnalyze(repoUrl)
    }
  }

  const getScoreColor = (score) => {
    if (score >= 80) return '#22c55e'
    if (score >= 60) return '#eab308'
    return '#ef4444'
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="user-dashboard">
        <div className="dashboard-loading">
          <div className="spinner"></div>
          <p>Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (error || !dashboardData) {
    return (
      <div className="user-dashboard">
        <div className="dashboard-error">
          <p>❌ {error || 'Failed to load dashboard'}</p>
          <button onClick={loadDashboard} className="btn btn-secondary">Retry</button>
        </div>
      </div>
    )
  }

  // If a history item is selected, show the detailed results
  if (selectedHistory) {
    return (
      <div className="user-dashboard">
        <div className="dashboard-header">
          <div className="profile-section">
            {dashboardData.avatar_url && (
              <img src={dashboardData.avatar_url} alt={dashboardData.username} className="profile-avatar" />
            )}
            <div className="profile-info">
              <h1>{dashboardData.username}</h1>
              {dashboardData.email && <p className="profile-email">{dashboardData.email}</p>}
            </div>
          </div>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <button 
              onClick={() => setSelectedHistory(null)}
              className="btn btn-secondary"
            >
              ← Back to Dashboard
            </button>
            {onSignOut && (
              <button onClick={onSignOut} className="btn btn-secondary">Sign Out</button>
            )}
          </div>
        </div>
        <div style={{ padding: '2rem 0' }}>
          <Results 
            results={selectedHistory.results}
            repoUrl={selectedHistory.repoUrl}
            onReset={() => setSelectedHistory(null)}
            userId={userId}
          />
        </div>
      </div>
    )
  }

  return (
    <div className="user-dashboard">
      <div className="dashboard-header">
        <div className="profile-section">
          {dashboardData.avatar_url && (
            <img src={dashboardData.avatar_url} alt={dashboardData.username} className="profile-avatar" />
          )}
          <div className="profile-info">
            <h1>{dashboardData.username}</h1>
            {dashboardData.email && <p className="profile-email">{dashboardData.email}</p>}
          </div>
        </div>
        {onSignOut && (
          <button onClick={onSignOut} className="btn btn-secondary">Sign Out</button>
        )}
      </div>

      <div className="dashboard-content">
        {/* Connected Repositories */}
        <section className="dashboard-section">
          <h2>Connected Repositories</h2>
          <div className="repos-grid">
            {dashboardData.repositories.map((repo) => (
              <div key={repo.id} className="repo-card">
                <div className="repo-info">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', width: '100%' }}>
                    <div style={{ flex: 1 }}>
                      <h3>{repo.repo_url.split('/').pop()}</h3>
                      <p className="repo-url">{repo.repo_url}</p>
                      <p className="repo-date">Connected {formatDate(repo.created_at)}</p>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDeleteRepository(repo.id, repo.repo_url)
                      }}
                      className="btn-delete-repo"
                      disabled={deletingRepoId === repo.id}
                      title="Remove repository"
                    >
                      {deletingRepoId === repo.id ? '...' : '×'}
                    </button>
                  </div>
                </div>
                <button 
                  onClick={() => handleAnalyzeRepo(repo.repo_url)}
                  className="btn btn-primary btn-small"
                  disabled={deletingRepoId === repo.id}
                >
                  Analyze Now
                </button>
              </div>
            ))}
            {/* Add Repository Card */}
            {showAddRepoForm ? (
              <div className="repo-card repo-add-form">
                <form onSubmit={handleAddRepository}>
                  <h3>Add Repository</h3>
                  <div className="form-group">
                    <label htmlFor="new-token">GitHub Token</label>
                    <input
                      id="new-token"
                      type="password"
                      value={newRepoToken}
                      onChange={(e) => setNewRepoToken(e.target.value)}
                      placeholder="github_pat_..."
                      className="form-input"
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="new-repo-url">Repository URL</label>
                    <input
                      id="new-repo-url"
                      type="url"
                      value={newRepoUrl}
                      onChange={(e) => setNewRepoUrl(e.target.value)}
                      placeholder="https://github.com/owner/repo"
                      className="form-input"
                      required
                    />
                  </div>
                  {error && (
                    <div className="form-error">
                      {error}
                    </div>
                  )}
                  <div className="form-actions">
                    <button
                      type="button"
                      onClick={() => {
                        setShowAddRepoForm(false)
                        setError(null)
                        setNewRepoToken('')
                        setNewRepoUrl('')
                      }}
                      className="btn btn-secondary btn-small"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="btn btn-primary btn-small"
                      disabled={addingRepo}
                    >
                      {addingRepo ? 'Adding...' : 'Add'}
                    </button>
                  </div>
                </form>
              </div>
            ) : (
              <div 
                className="repo-card repo-add-card"
                onClick={() => setShowAddRepoForm(true)}
              >
                <div className="repo-add-icon">+</div>
                <p className="repo-add-text">Add Repository</p>
              </div>
            )}
          </div>
        </section>

        {/* Analysis History */}
        <section className="dashboard-section">
          <h2>Analysis History</h2>
          {dashboardData.analysis_history.length === 0 ? (
            <div className="empty-state">
              <p>No analyses yet. Analyze a repository to see history here.</p>
            </div>
          ) : (
            <div className="history-list">
              {dashboardData.analysis_history.map((analysis) => (
                <div 
                  key={analysis.id} 
                  className={`history-item ${analysis.metadata ? 'history-item-clickable' : ''}`}
                  onClick={() => {
                    if (analysis.metadata) {
                      // Convert history metadata to Results format
                      // Ensure discrepancies are properly formatted
                      let discrepancies = analysis.metadata.discrepancies || []
                      
                      // If discrepancies is not an array, try to extract it
                      if (!Array.isArray(discrepancies)) {
                        discrepancies = []
                      }
                      
                      const resultsData = {
                        status: 'success',
                        discrepancies: discrepancies,
                        summary: `Trust score ${analysis.trust_score}%. Issues found: ${analysis.discrepancies_count}.`,
                        metadata: {
                          ...analysis.metadata,
                          trust_score: analysis.trust_score,
                          total_functions: analysis.total_functions,
                          verified: analysis.verified_count
                        }
                      }
                      
                      console.log('Loading history analysis:', {
                        discrepanciesCount: discrepancies.length,
                        metadata: analysis.metadata,
                        resultsData
                      })
                      
                      setSelectedHistory({ results: resultsData, repoUrl: analysis.repo_url })
                    }
                  }}
                  style={{ cursor: analysis.metadata ? 'pointer' : 'default' }}
                >
                  <div className="history-main">
                    <div className="history-repo">
                      <h3>{analysis.repo_url.split('/').pop()}</h3>
                      <p className="history-url">{analysis.repo_url}</p>
                    </div>
                    <div className="history-score">
                      <div 
                        className="history-score-circle"
                        style={{ borderColor: getScoreColor(analysis.trust_score) }}
                      >
                        <span style={{ color: getScoreColor(analysis.trust_score) }}>
                          {analysis.trust_score}%
                        </span>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDeleteHistory(analysis.id)
                        }}
                        className="btn-delete-history"
                        disabled={deletingId === analysis.id}
                        title="Delete this analysis"
                      >
                        {deletingId === analysis.id ? '...' : '×'}
                      </button>
                    </div>
                  </div>
                  <div className="history-stats">
                    <div className="history-stat">
                      <span className="stat-label">Functions:</span>
                      <span className="stat-value">{analysis.total_functions}</span>
                    </div>
                    <div className="history-stat">
                      <span className="stat-label">Verified:</span>
                      <span className="stat-value" style={{ color: '#22c55e' }}>
                        {analysis.verified_count}
                      </span>
                    </div>
                    <div className="history-stat">
                      <span className="stat-label">Issues:</span>
                      <span className="stat-value" style={{ color: '#ef4444' }}>
                        {analysis.discrepancies_count}
                      </span>
                    </div>
                    <div className="history-date">
                      {formatDate(analysis.created_at)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  )
}

export default UserDashboard
