import { useState } from 'react'
import './RepoInput.css'

function RepoInput({ onSubmit }) {
  const [url, setUrl] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (url.trim()) {
      onSubmit(url.trim())
    }
  }

  return (
    <div className="repo-input-container">
      <div className="input-card">
        <h2>Analyze GitHub Repository</h2>
        <p className="input-description">
          Enter a GitHub repository URL to verify that code and documentation match
        </p>
        
        <form onSubmit={handleSubmit} className="repo-input-form">
          <div className="input-group">
            <label htmlFor="repo-url">Repository URL</label>
            <input
              id="repo-url"
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://github.com/user/repo"
              className="repo-input"
              required
            />
          </div>
          
          <button type="submit" className="btn btn-primary">
            Start Analysis
          </button>
        </form>
      </div>
    </div>
  )
}

export default RepoInput