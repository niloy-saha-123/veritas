import { useState, useEffect } from 'react'
import './SignIn.css'

function SignIn({ onSignIn, onTokenSave, user: propUser }) {
  const [showTokenForm, setShowTokenForm] = useState(false)
  const [token, setToken] = useState('')
  const [repoUrl, setRepoUrl] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [localUser, setLocalUser] = useState(null)

  // Use propUser if available, otherwise use localUser
  const currentUser = propUser || localUser

  // Clear localUser when propUser is cleared (user signed out)
  useEffect(() => {
    if (!propUser) {
      setLocalUser(null)
      setShowTokenForm(false)
    }
  }, [propUser])

  useEffect(() => {
    // Check if user is in URL params (from OAuth callback)
    const urlParams = new URLSearchParams(window.location.search)
    const userId = urlParams.get('user_id')
    const username = urlParams.get('username')
    
    if (userId && username) {
      const userData = { id: parseInt(userId), username }
      // Set local user
      setLocalUser(userData)
      if (onSignIn) {
        onSignIn(userData)
      }
      // Always show token form when coming from OAuth callback
      setShowTokenForm(true)
      // Clean URL
      window.history.replaceState({}, document.title, window.location.pathname)
    }
  }, [onSignIn])

  const handleGitHubSignIn = (e) => {
    if (e) {
      e.preventDefault()
      e.stopPropagation()
    }
    console.log('Sign in clicked, redirecting to GitHub OAuth...')
    try {
      // Redirect to backend OAuth endpoint
      window.location.href = 'http://localhost:8000/api/v1/auth/github'
    } catch (err) {
      console.error('Failed to redirect:', err)
      alert('Failed to connect to server. Please make sure the backend is running on http://localhost:8000')
    }
  }

  const handleSaveToken = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError(null)

    try {
      if (!currentUser || !currentUser.id) {
        throw new Error('User not found. Please sign in again.')
      }

      console.log('Saving token for user:', currentUser.id)

      const response = await fetch('http://localhost:8000/api/v1/auth/save-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: token.trim(),
          repo_url: repoUrl.trim(),
          user_id: currentUser.id
        })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }))
        throw new Error(errorData.detail || `Failed to save token: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()
      if (data.success) {
        if (onTokenSave) {
          onTokenSave({ token, repoUrl, userId: currentUser.id })
        }
        setShowTokenForm(false)
        setToken('')
        setRepoUrl('')
      } else {
        throw new Error(data.message || 'Failed to save token')
      }
    } catch (err) {
      console.error('Token save error:', err)
      // More descriptive error message
      if (err.message.includes('fetch')) {
        setError('Failed to connect to server. Make sure the backend is running on http://localhost:8000')
      } else {
        setError(err.message || 'Failed to save token')
      }
    } finally {
      setSaving(false)
    }
  }

  // Always show token form modal if user is set and form should be visible
  if (showTokenForm && currentUser) {
    return (
      <>
        <div className="sign-in-modal">
        <div className="sign-in-card">
          <h2>Welcome, {currentUser.username}!</h2>
          <p className="sign-in-subtitle">
            To enable automatic issue creation, please provide your GitHub fine-grained token with issue read/write access.
          </p>
          
          <form onSubmit={handleSaveToken} className="token-form">
            <div className="form-group">
              <label htmlFor="token">GitHub Fine-Grained Token</label>
              <input
                id="token"
                type="password"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                placeholder="github_pat_..."
                className="form-input"
                required
              />
              <p className="form-help">
                Create a fine-grained token at{' '}
                <a href="https://github.com/settings/tokens?type=beta" target="_blank" rel="noopener noreferrer">
                  GitHub Settings
                </a>
                {' '}with <strong>Issues: Read and write</strong> permission
              </p>
            </div>

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
              <p className="form-help">
                The repository URL that your token has access to
              </p>
            </div>

            {error && (
              <div className="form-error">
                {error}
              </div>
            )}

            <div className="form-actions">
              <button
                type="button"
                onClick={() => setShowTokenForm(false)}
                className="btn btn-secondary"
              >
                Skip for now
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={saving}
              >
                {saving ? 'Saving...' : 'Save Token'}
              </button>
            </div>
          </form>
        </div>
      </div>
      </>
    )
  }

  // If user is already set (from prop), don't show sign-in button
  if (propUser) {
    return null
  }

  // Show sign-in button when user is not logged in
  return (
    <button 
      onClick={handleGitHubSignIn} 
      className="btn-sign-in"
      type="button"
    >
      <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" style={{ marginRight: '0.5rem' }}>
        <path d="M12 2C6.48 2 2 6.48 2 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.08 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12c0-5.52-4.48-10-10-10z"/>
      </svg>
      Sign in with GitHub
    </button>
  )
}

export default SignIn
