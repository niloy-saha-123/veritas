import './AnalysisProgress.css'

function AnalysisProgress({ repoUrl }) {
  return (
    <div className="progress-container">
      <div className="progress-card">
        <div className="progress-header">
          <div className="spinner"></div>
          <h2>Analyzing Repository</h2>
        </div>
        
        <div className="repo-info">
          <p className="repo-url">{repoUrl}</p>
        </div>

        <div className="progress-steps">
          <div className="progress-step">
            <div className="step-icon">📥</div>
            <div className="step-content">
              <h3>Cloning Repository</h3>
              <p>Downloading repository files...</p>
            </div>
          </div>

          <div className="progress-step">
            <div className="step-icon">🔍</div>
            <div className="step-content">
              <h3>Discovering Files</h3>
              <p>Identifying code and documentation files...</p>
            </div>
          </div>

          <div className="progress-step">
            <div className="step-icon">📝</div>
            <div className="step-content">
              <h3>Extracting Functions</h3>
              <p>Parsing code and documentation...</p>
            </div>
          </div>

          <div className="progress-step">
            <div className="step-icon">🧠</div>
            <div className="step-content">
              <h3>Running Analysis</h3>
              <p>Comparing code and documentation with AI...</p>
            </div>
          </div>
        </div>

        <div className="progress-note">
          <p>This may take a few minutes for large repositories.</p>
          <p className="note-detail">Check the server console for detailed progress logs.</p>
        </div>
      </div>
    </div>
  )
}

export default AnalysisProgress