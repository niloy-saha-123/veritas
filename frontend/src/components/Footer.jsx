import React from 'react';
import { Github } from 'lucide-react';
import { COLORS } from '../constants/constants';

// Footer Component
export const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer style={{
      borderTop: `1px solid ${COLORS.border}`,
      padding: '40px 32px',
      backgroundColor: COLORS.canvas
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '32px'
      }} className="footer-content">
        <div style={{
          fontFamily: 'IBM Plex Sans, sans-serif',
          fontSize: '14px',
          color: COLORS.muted
        }}>
          © {currentYear} Veritas.dev. All rights reserved.
        </div>

        <nav style={{
          display: 'flex',
          gap: '32px',
          alignItems: 'center',
          fontFamily: 'IBM Plex Sans, sans-serif',
          fontSize: '14px',
          flexWrap: 'wrap'
        }}>
          {['How it Works', 'Features'].map((item) => (
            <a 
              key={item}
              href={`#${item.toLowerCase().replace(/\s/g, '-')}`}
              style={{
                color: COLORS.muted,
                textDecoration: 'none',
                transition: 'color 0.2s ease'
              }}
              onMouseEnter={(e) => e.target.style.color = COLORS.ink}
              onMouseLeave={(e) => e.target.style.color = COLORS.muted}
            >
              {item}
            </a>
          ))}
          <a 
            href="https://github.com/niloy-saha-123/veritas"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              color: COLORS.muted,
              textDecoration: 'none',
              transition: 'color 0.2s ease'
            }}
            onMouseEnter={(e) => e.target.style.color = COLORS.ink}
            onMouseLeave={(e) => e.target.style.color = COLORS.muted}
          >
            GitHub
          </a>
        </nav>

        <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
          <a 
            href="#twitter" 
            aria-label="Twitter" 
            style={{ 
              color: COLORS.muted, 
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = COLORS.ink;
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = COLORS.muted;
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M4 4l11.733 16h4.267l-11.733 -16z" />
              <path d="M4 20l6.768 -6.768m2.46 -2.46l6.772 -6.772" />
            </svg>
          </a>
          <a 
            href="https://github.com/niloy-saha-123/veritas"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="GitHub" 
            style={{ 
              color: COLORS.muted, 
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = COLORS.ink;
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = COLORS.muted;
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            <Github size={20} />
          </a>
          <a 
            href="#discord" 
            aria-label="Discord" 
            style={{ 
              color: COLORS.muted, 
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = COLORS.ink;
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = COLORS.muted;
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515a.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0a12.64 12.64 0 0 0-.617-1.25a.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057a19.9 19.9 0 0 0 5.993 3.03a.078.078 0 0 0 .084-.028a14.09 14.09 0 0 0 1.226-1.994a.076.076 0 0 0-.041-.106a13.107 13.107 0 0 1-1.872-.892a.077.077 0 0 1-.008-.128a10.2 10.2 0 0 0 .372-.292a.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127a12.299 12.299 0 0 1-1.873.892a.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028a19.839 19.839 0 0 0 6.002-3.03a.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419c0-1.333.956-2.419 2.157-2.419c1.21 0 2.176 1.096 2.157 2.42c0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419c0-1.333.955-2.419 2.157-2.419c1.21 0 2.176 1.096 2.157 2.42c0 1.333-.946 2.418-2.157 2.418z"/>
            </svg>
          </a>
        </div>
      </div>

      <style>{`
        @media (max-width: 768px) {
          .footer-content {
            flex-direction: column;
            text-align: center;
            gap: 24px !important;
          }
          .footer-content nav {
            flex-direction: column;
            gap: 16px !important;
          }
        }
      `}</style>
    </footer>
  );
};

