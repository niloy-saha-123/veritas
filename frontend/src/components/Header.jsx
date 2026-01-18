import React, { useState, useEffect } from 'react';
import { Menu, X } from 'lucide-react';
import { COLORS } from '../constants/constants';

// Header Component
export const Header = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 0);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header 
      style={{
        position: 'sticky',
        top: 0,
        height: '72px',
        backgroundColor: COLORS.canvas,
        borderBottom: `1px solid ${isScrolled ? COLORS.border : 'transparent'}`,
        transition: 'border-color 0.2s ease',
        zIndex: 1000,
        padding: '0'
      }}
    >
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        padding: '0 32px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '100%'
      }}>
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <span style={{ 
            fontFamily: 'Space Grotesk, sans-serif', 
            fontSize: '24px', 
            fontWeight: 700,
            color: COLORS.ink 
          }}>
            Veritas
          </span>
        </div>

        {/* Desktop Nav */}
        <nav style={{ 
          display: 'flex', 
          gap: '40px',
          fontSize: '15px',
          fontFamily: 'IBM Plex Sans, sans-serif'
        }} className="desktop-nav">
          {['Features', 'How it Works'].map(item => (
            <a 
              key={item}
              href={`#${item.toLowerCase().replace(/\s/g, '-')}`}
              style={{
                color: COLORS.muted,
                textDecoration: 'none',
                transition: 'color 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.target.style.color = COLORS.ink;
              }}
              onMouseLeave={(e) => {
                e.target.style.color = COLORS.muted;
              }}
            >
              {item}
            </a>
          ))}
        </nav>

        {/* Desktop Right */}
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }} className="desktop-nav">
          <a href="#signin" style={{ 
            color: COLORS.muted, 
            textDecoration: 'none',
            fontSize: '15px',
            fontFamily: 'IBM Plex Sans, sans-serif',
            transition: 'color 0.2s ease'
          }}
          onMouseEnter={(e) => e.target.style.color = COLORS.ink}
          onMouseLeave={(e) => e.target.style.color = COLORS.muted}
          >
            Sign in
          </a>
          <button style={{
            backgroundColor: COLORS.ink,
            color: COLORS.canvas,
            border: 'none',
            borderRadius: '8px',
            padding: '10px 20px',
            fontSize: '15px',
            fontFamily: 'IBM Plex Sans, sans-serif',
            fontWeight: 500,
            cursor: 'pointer',
            transition: 'transform 0.1s ease'
          }}
          onMouseDown={(e) => e.target.style.transform = 'scale(0.98)'}
          onMouseUp={(e) => e.target.style.transform = 'scale(1)'}
          onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
          >
            Get Started
          </button>
        </div>

        {/* Mobile Menu Button */}
        <button 
          className="mobile-menu-btn"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          style={{
            display: 'none',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            padding: '8px'
          }}
        >
          {isMobileMenuOpen ? <X size={24} color={COLORS.ink} /> : <Menu size={24} color={COLORS.ink} />}
        </button>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="mobile-menu" style={{
          position: 'absolute',
          top: '72px',
          left: 0,
          right: 0,
          backgroundColor: COLORS.canvas,
          borderBottom: `1px solid ${COLORS.border}`,
          padding: '24px 32px',
          display: 'none',
          flexDirection: 'column',
          gap: '24px'
        }}>
          {['Features', 'How it Works'].map(item => (
            <a 
              key={item}
              href={`#${item.toLowerCase().replace(/\s/g, '-')}`}
              style={{
                color: COLORS.ink,
                textDecoration: 'none',
                fontSize: '16px',
                fontFamily: 'IBM Plex Sans, sans-serif'
              }}
              onClick={() => setIsMobileMenuOpen(false)}
            >
              {item}
            </a>
          ))}
          <button style={{
            backgroundColor: COLORS.ink,
            color: COLORS.canvas,
            border: 'none',
            borderRadius: '8px',
            padding: '12px 24px',
            fontSize: '16px',
            fontFamily: 'IBM Plex Sans, sans-serif',
            fontWeight: 500,
            cursor: 'pointer',
            marginTop: '8px'
          }}>
            Get Started
          </button>
        </div>
      )}

      <style>{`
        @media (max-width: 1024px) {
          .desktop-nav {
            display: none !important;
          }
          .mobile-menu-btn {
            display: block !important;
          }
          .mobile-menu {
            display: flex !important;
          }
        }
      `}</style>
    </header>
  );
};

