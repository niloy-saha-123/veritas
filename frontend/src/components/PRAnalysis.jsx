import { useState } from 'react'
import './PRAnalysis.css'

function PRAnalysis({ userId, onBack }) {
  const [repoUrl, setRepoUrl] = useState('')
  const [prNumber, setPrNumber] = useState('')
  const [githubToken, setGithubToken] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [postingComment, setPostingComment] = useState(false)
  const [commentPosted, setCommentPosted] = useState(false)

  const handleAnalyze = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResults(null)
    setCommentPosted(false)

    try {
      const response = await fetch('http://localhost:8000/api/v1/analyze/pr', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          repo_url: repoUrl,
          pr_number: parseInt(prNumber),
          user_id: userId || null,
          github_token: githubToken || null,  // Use provided token or fallback to stored token
          post_comment: false
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || data.error || 'Failed to analyze PR')
      }

      setResults(data)
    } catch (err) {
      setError(err.message || 'Failed to analyze PR')
      console.error('PR Analysis error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handlePostComment = async () => {
    if (!results) return

    setPostingComment(true)
    setError(null)

    try {
      const response = await fetch('http://localhost:8000/api/v1/analyze/pr/comment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          repo_url: repoUrl,
          pr_number: parseInt(prNumber),
          user_id: userId || null,
          github_token: githubToken || null  // Use provided token or fallback to stored token
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || data.error || 'Failed to post comment')
      }

      setCommentPosted(true)
      if (data.comment_url) {
        setResults({ ...results, comment_url: data.comment_url })
      }
    } catch (err) {
      setError(err.message || 'Failed to post comment')
      console.error('Post comment error:', err)
    } finally {
      setPostingComment(false)
    }
  }

  const getScoreColor = (score) => {
    if (score >= 80) return '#22c55e'
    if (score >= 60) return '#eab308'
    return '#ef4444'
  }

  const getScoreLabel = (score) => {
    if (score >= 80) return 'Excellent'
    if (score >= 60) return 'Good'
    if (score >= 40) return 'Needs Improvement'
    return 'Poor'
  }

  return (
    <div className="pr-analysis-container">
      <div className="pr-analysis-header">
        <div className="pr-analysis-title">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span style={{ fontSize: '2rem' }}>👑</span>
            <h2>PR Analysis</h2>
            <span className="premium-badge-inline">Premium</span>
          </div>
          <p className="pr-analysis-subtitle">
            Analyze Pull Requests for documentation issues.<br />
            <strong>Requirements:</strong> Fine-grained GitHub token with Pull Request (read/write) and Issue (read/write) permissions for the repository.
          </p>
          <div className="pr-requirements-box">
            <h4>📋 Required Token Permissions:</h4>
            <ul>
              <li>✅ Pull Requests: <strong>Read and Write</strong></li>
              <li>✅ Issues: <strong>Read and Write</strong></li>
              <li>✅ Repository: <strong>Read</strong> (for accessing PR files)</li>
            </ul>
            <p className="pr-note">
              <strong>Note:</strong> Make sure you've connected a repository with a fine-grained token that has these permissions. The token will be automatically used from your connected repositories.
            </p>
          </div>
        </div>
        {onBack && (
          <button onClick={onBack} className="btn btn-secondary btn-small">
            ← Back
          </button>
        )}
      </div>

      {!results && (
        <form onSubmit={handleAnalyze} className="pr-analysis-form">
          <div className="form-group">
            <label htmlFor="repo-url">Repository URL</label>
            <input
              id="repo-url"
              type="url"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              placeholder="https://github.com/owner/repo"
              className="form-input"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="pr-number">Pull Request Number</label>
            <input
              id="pr-number"
              type="number"
              value={prNumber}
              onChange={(e) => setPrNumber(e.target.value)}
              placeholder="123"
              className="form-input"
              required
              min="1"
            />
          </div>
          <div className="form-group">
            <label htmlFor="github-token">
              GitHub Fine-Grained Token 
              <span style={{ color: '#666', fontSize: '0.85rem', fontWeight: 'normal', marginLeft: '0.5rem' }}>
                (Optional - will use stored token if not provided)
              </span>
            </label>
            <input
              id="github-token"
              type="password"
              value={githubToken}
              onChange={(e) => setGithubToken(e.target.value)}
              placeholder="github_pat_..."
              className="form-input"
            />
            <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '0.5rem', marginBottom: 0 }}>
              Required permissions: Pull Requests (read/write), Issues (read/write), Repository (read)
            </p>
          </div>
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
          <button 
            type="submit" 
            className="btn btn-primary btn-large"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner-small"></span>
                Analyzing PR...
              </>
            ) : (
              'Analyze PR'
            )}
          </button>
        </form>
      )}

      {results && (
        <div className="pr-analysis-results">
          <div className="pr-results-header">
            <div>
              <h3>Analysis Results</h3>
              <p className="pr-info">
                PR #{results.pr_number} · {results.files_analyzed} file(s) analyzed
              </p>
            </div>
            <div className="pr-results-actions">
              {!commentPosted && !results.comment_url && (
                <button
                  onClick={handlePostComment}
                  className="btn btn-primary"
                  disabled={postingComment}
                >
                  {postingComment ? (
                    <>
                      <span className="spinner-small"></span>
                      Posting...
                    </>
                  ) : (
                    '💬 Post Comment to PR'
                  )}
                </button>
              )}
              {(commentPosted || results.comment_url) && (
                <a
                  href={results.comment_url || '#'}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-secondary"
                >
                  ✅ View Comment on GitHub
                </a>
              )}
              <button
                onClick={() => {
                  setResults(null)
                  setError(null)
                  setCommentPosted(false)
                }}
                className="btn btn-secondary"
              >
                New Analysis
              </button>
            </div>
          </div>

          <div className="pr-score-card">
            <div className="pr-score-display">
              <div className="pr-score-circle" style={{ borderColor: getScoreColor(results.trust_score) }}>
                <span className="pr-score-value" style={{ color: getScoreColor(results.trust_score) }}>
                  {results.trust_score}%
                </span>
              </div>
              <div className="pr-score-info">
                <h3>Trust Score</h3>
                <p className="pr-score-label" style={{ color: getScoreColor(results.trust_score) }}>
                  {getScoreLabel(results.trust_score)}
                </p>
              </div>
            </div>
          </div>

          {results.new_functions && results.new_functions.length > 0 && (
            <div className="pr-section-card">
              <h4>✨ New Functions ({results.new_functions.length})</h4>
              <div className="pr-list">
                {results.new_functions.map((func, idx) => (
                  <div key={idx} className="pr-item">
                    <div className="pr-item-header">
                      <code className="pr-function-name">{func.name}</code>
                      <span className="pr-file-name">{func.file}</span>
                    </div>
                    {func.signature && (
                      <pre className="pr-code-snippet">{func.signature}</pre>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {results.modified_functions && results.modified_functions.length > 0 && (
            <div className="pr-section-card">
              <h4>🔄 Modified Functions ({results.modified_functions.length})</h4>
              <div className="pr-list">
                {results.modified_functions.map((func, idx) => (
                  <div key={idx} className="pr-item">
                    <div className="pr-item-header">
                      <code className="pr-function-name">{func.name}</code>
                      <span className="pr-file-name">{func.file}</span>
                    </div>
                    <div className="pr-diff">
                      <div className="pr-diff-old">
                        <strong>Old:</strong>
                        <pre>{func.old_signature}</pre>
                      </div>
                      <div className="pr-diff-new">
                        <strong>New:</strong>
                        <pre>{func.new_signature}</pre>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {results.missing_docs && results.missing_docs.length > 0 && (
            <div className="pr-section-card pr-warning">
              <h4>⚠️ Missing Documentation ({results.missing_docs.length})</h4>
              <div className="pr-list">
                {results.missing_docs.map((doc, idx) => (
                  <div key={idx} className="pr-item">
                    <div className="pr-item-header">
                      <code className="pr-function-name">{doc.function}</code>
                      <span className="pr-file-name">{doc.file}</span>
                    </div>
                    <p className="pr-warning-text">This function needs documentation</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {results.discrepancies && results.discrepancies.length > 0 && (
            <div className="pr-section-card pr-error">
              <h4>🔴 Documentation Discrepancies ({results.discrepancies.length})</h4>
              <div className="pr-discrepancies-list">
                {results.discrepancies.map((disc, idx) => (
                  <div key={idx} className={`pr-discrepancy-item severity-${disc.severity}`}>
                    <div className="pr-discrepancy-header">
                      <span className={`pr-severity-badge severity-${disc.severity}`}>
                        {disc.severity?.toUpperCase() || 'UNKNOWN'}
                      </span>
                      <span className="pr-discrepancy-type">{disc.type?.replace('_', ' ') || 'Issue'}</span>
                    </div>
                    <div className="pr-discrepancy-content">
                      <p className="pr-discrepancy-description">{disc.description}</p>
                      {disc.location && (
                        <p className="pr-discrepancy-location">📍 {disc.location}</p>
                      )}
                      {disc.suggestion && (
                        <div className="pr-discrepancy-suggestion">
                          <strong>💡 Suggestion:</strong> {disc.suggestion}
                        </div>
                      )}
                      {(disc.code_snippet || disc.doc_snippet) && (
                        <div className="pr-discrepancy-snippets">
                          {disc.code_snippet && (
                            <div className="pr-snippet pr-code-snippet">
                              <strong>Code:</strong>
                              <pre>{disc.code_snippet}</pre>
                            </div>
                          )}
                          {disc.doc_snippet && (
                            <div className="pr-snippet pr-doc-snippet">
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

          {(!results.new_functions?.length && 
            !results.modified_functions?.length && 
            !results.missing_docs?.length && 
            !results.discrepancies?.length) && (
            <div className="pr-success-message">
              <div className="pr-success-icon">✨</div>
              <h3>Perfect Match!</h3>
              <p>No documentation issues found in this PR. Great job! 🎉</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default PRAnalysis
