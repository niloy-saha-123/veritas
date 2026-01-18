import './Footer.css'

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-left">
          <p className="footer-copyright">© 2026 Veritas.dev. All rights reserved.</p>
        </div>
        <div className="footer-right">
          <a href="#how-it-works" className="footer-link" onClick={(e) => {
            e.preventDefault()
            document.querySelector('#how-it-works')?.scrollIntoView({ behavior: 'smooth' })
          }}>How it Works</a>
          <a href="#features" className="footer-link" onClick={(e) => {
            e.preventDefault()
            document.querySelector('#features')?.scrollIntoView({ behavior: 'smooth' })
          }}>Features</a>
          <a href="https://github.com/niloy-saha-123/veritas" target="_blank" rel="noopener noreferrer" className="footer-link">GitHub</a>
        </div>
      </div>
    </footer>
  )
}

export default Footer
