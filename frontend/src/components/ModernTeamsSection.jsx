import React, { useState, useEffect, useRef } from 'react';
import { COLORS } from '../constants/constants';

const languages = {
    Python: {
      code: `def calculate_total(items: list, discount: float = 0.0):
    """
    Calculate total price with discount.
    
    Args:
        items: List of item prices
        discount: Discount percentage (0-1)
    
    Returns:
        Total price after discount
    """
    subtotal = sum(items)
    return subtotal * (1 - discount)`,
      files: ['utils.py', 'calculator.py', 'pricing.py']
    },
    TypeScript: {
      code: `interface User {
  id: number;
  email: string;
  role: 'admin' | 'user';
}

function getUserById(id: number): User | null {
  // Returns user or null if not found
  return users.find(u => u.id === id) || null;
}`,
      files: ['types.ts', 'user.ts', 'api.ts']
    },
    Java: {
      code: `public class PaymentProcessor {
    /**
     * Process payment for given amount.
     * 
     * @param amount Payment amount in cents
     * @param currency Currency code (USD, EUR)
     * @return Transaction ID or null if failed
     */
    public String processPayment(int amount, String currency) {
        if (amount <= 0) return null;
        return paymentGateway.charge(amount, currency);
    }
}`,
      files: ['Payment.java', 'Processor.java', 'Main.java']
    },
    JSON: {
      code: `{
  "api": {
    "version": "2.0",
    "endpoints": [
      {
        "path": "/api/users",
        "method": "GET",
        "params": ["page", "limit"],
        "returns": "User[]"
      }
    ]
  }
}`,
      files: ['api.json', 'config.json', 'schema.json']
    },
    Markdown: {
      code: `# API Documentation

## getUserById(id)

Fetches a user by their ID.

**Parameters:**
- \`id\` (number): User identifier

**Returns:**
- User object or null if not found`,
      files: ['README.md', 'api.md', 'docs.md']
    }
};

// Built for Modern Teams Section
export const ModernTeamsSection = () => {
  const [selectedLanguage, setSelectedLanguage] = useState('Java');
  const [isVisible, setIsVisible] = useState(false);
  const [trustScore, setTrustScore] = useState(0);
  const [displayedCode, setDisplayedCode] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const sectionRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          // Animate trust score from 0 to 92
          animateTrustScore();
        }
      },
      { threshold: 0.2 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, []);

  const animateTrustScore = () => {
    const duration = 2000; // 2 seconds
    const startTime = Date.now();
    const startValue = 0;
    const targetValue = 92;

    const updateScore = () => {
      const now = Date.now();
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function for smooth animation
      const easeOutCubic = 1 - Math.pow(1 - progress, 3);
      const currentValue = Math.floor(startValue + (targetValue - startValue) * easeOutCubic);
      
      setTrustScore(currentValue);

      if (progress < 1) {
        requestAnimationFrame(updateScore);
      } else {
        setTrustScore(targetValue);
      }
    };

    requestAnimationFrame(updateScore);
  };

  useEffect(() => {
    // Reset and type out code when language changes
    setIsTyping(true);
    setDisplayedCode('');
    const code = languages[selectedLanguage].code;
    let currentIndex = 0;

    const typeCode = () => {
      if (currentIndex < code.length) {
        setDisplayedCode(code.substring(0, currentIndex + 1));
        currentIndex++;
        setTimeout(typeCode, 30); // Typing speed
      } else {
        setIsTyping(false);
      }
    };

    const timer = setTimeout(typeCode, 100);
    return () => clearTimeout(timer);
  }, [selectedLanguage]);

  return (
    <section ref={sectionRef} style={{
      padding: '80px 32px',
      backgroundColor: COLORS.canvas
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto'
      }}>
        <h2 style={{
          fontFamily: 'Space Grotesk, sans-serif',
          fontSize: 'clamp(32px, 5vw, 48px)',
          lineHeight: '1.2',
          fontWeight: 700,
          color: COLORS.ink,
          textAlign: 'center',
          margin: '0 0 64px 0'
        }}>
          Built for Modern Teams
        </h2>

        <div style={{
          display: 'grid',
          gridTemplateColumns: '1.3fr 0.7fr',
          gap: '48px',
          alignItems: 'stretch'
        }} className="modern-teams-grid">
          {/* Left: Multi-Language Support */}
          <div style={{
            backgroundColor: '#FFFFFF',
            border: `1px solid ${COLORS.border}`,
            borderRadius: '12px',
            padding: '40px',
            opacity: isVisible ? 1 : 0,
            transform: isVisible ? 'translateX(0)' : 'translateX(-30px)',
            transition: 'all 0.6s ease-out',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <h3 style={{
              fontFamily: 'Space Grotesk, sans-serif',
              fontSize: '28px',
              fontWeight: 700,
              color: COLORS.ink,
              margin: '0 0 32px 0'
            }}>
              Multi-Language Support
            </h3>

            {/* Language Tabs */}
            <div style={{
              display: 'flex',
              gap: '12px',
              marginBottom: '24px',
              flexWrap: 'wrap'
            }}>
              {Object.keys(languages).map((lang) => (
                <button
                  key={lang}
                  onClick={() => setSelectedLanguage(lang)}
                  style={{
                    padding: '10px 20px',
                    fontSize: '14px',
                    fontFamily: 'IBM Plex Sans, sans-serif',
                    fontWeight: 500,
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    backgroundColor: selectedLanguage === lang ? COLORS.ink : COLORS.panelLight,
                    color: selectedLanguage === lang ? COLORS.canvas : COLORS.muted,
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => {
                    if (selectedLanguage !== lang) {
                      e.target.style.backgroundColor = COLORS.panelMid;
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (selectedLanguage !== lang) {
                      e.target.style.backgroundColor = COLORS.panelLight;
                    }
                  }}
                >
                  {lang}
                </button>
              ))}
            </div>

            {/* Code Preview */}
            <div style={{
              backgroundColor: COLORS.canvas,
              border: `1px solid ${COLORS.border}`,
              borderRadius: '8px',
              padding: '24px',
              minHeight: '280px',
              flex: 1,
              display: 'flex',
              flexDirection: 'column'
            }}>
              <div style={{
                display: 'flex',
                gap: '12px',
                marginBottom: '16px',
                fontSize: '13px',
                fontFamily: 'JetBrains Mono, monospace',
                color: COLORS.muted,
                flexWrap: 'wrap'
              }}>
                {languages[selectedLanguage].files.map((file, index) => (
                  <span
                    key={file}
                    style={{
                      borderBottom: index === languages[selectedLanguage].files.length - 1 
                        ? `2px solid ${COLORS.ink}` 
                        : 'none',
                      color: index === languages[selectedLanguage].files.length - 1 
                        ? COLORS.ink 
                        : COLORS.muted,
                      paddingBottom: index === languages[selectedLanguage].files.length - 1 
                        ? '4px' 
                        : '0',
                      cursor: 'pointer',
                      transition: 'color 0.2s ease'
                    }}
                    onMouseEnter={(e) => {
                      if (index !== languages[selectedLanguage].files.length - 1) {
                        e.target.style.color = COLORS.ink;
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (index !== languages[selectedLanguage].files.length - 1) {
                        e.target.style.color = COLORS.muted;
                      }
                    }}
                  >
                    {file}
                  </span>
                ))}
              </div>
              <pre style={{
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '13px',
                color: COLORS.ink,
                margin: 0,
                whiteSpace: 'pre-wrap',
                opacity: 1,
                lineHeight: '1.6',
                flex: 1
              }}>
                {displayedCode}
                {isTyping && <span style={{ 
                  animation: 'blink 1s infinite',
                  marginLeft: '2px'
                }}>|</span>}
              </pre>
            </div>
          </div>

          {/* Right: Stats Cards */}
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '24px'
          }}>
            {/* Trust Score Card */}
            <div style={{
              backgroundColor: '#FFFFFF',
              border: `1px solid ${COLORS.border}`,
              borderRadius: '12px',
              padding: '32px',
              textAlign: 'center',
              opacity: isVisible ? 1 : 0,
              transform: isVisible ? 'translateY(0)' : 'translateY(30px)',
              transition: 'all 0.6s ease-out 0.2s'
            }}>
              <div style={{
                width: '100px',
                height: '100px',
                margin: '0 auto 16px',
                position: 'relative'
              }}>
                <svg width="100" height="100" viewBox="0 0 100 100">
                  <circle
                    cx="50"
                    cy="50"
                    r="45"
                    fill="none"
                    stroke={COLORS.panelLight}
                    strokeWidth="8"
                  />
                  <circle
                    cx="50"
                    cy="50"
                    r="45"
                    fill="none"
                    stroke={COLORS.ink}
                    strokeWidth="8"
                    strokeDasharray="283"
                    strokeDashoffset={isVisible ? 283 * (1 - trustScore / 100) : 283}
                    strokeLinecap="round"
                    transform="rotate(-90 50 50)"
                    style={{
                      transition: 'stroke-dashoffset 0.1s linear'
                    }}
                  />
                </svg>
                <div style={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                  fontFamily: 'Space Grotesk, sans-serif',
                  fontSize: '32px',
                  fontWeight: 700,
                  color: COLORS.ink
                }}>
                  {trustScore}%
                </div>
              </div>
              <div style={{
                fontFamily: 'IBM Plex Sans, sans-serif',
                fontSize: '16px',
                color: COLORS.muted
              }}>
                Trust Score
              </div>
            </div>

            {/* IDE Integration Card */}
            <div style={{
              backgroundColor: '#FFFFFF',
              border: `1px solid ${COLORS.border}`,
              borderRadius: '12px',
              padding: '32px',
              textAlign: 'center',
              opacity: isVisible ? 1 : 0,
              transform: isVisible ? 'translateY(0)' : 'translateY(30px)',
              transition: 'all 0.6s ease-out 0.3s'
            }}>
              <div style={{
                fontSize: '40px',
                marginBottom: '16px'
              }}>
                ⌘
              </div>
              <div style={{
                fontFamily: 'IBM Plex Sans, sans-serif',
                fontSize: '16px',
                fontWeight: 600,
                color: COLORS.ink,
                marginBottom: '8px'
              }}>
                GitHub App Integration
              </div>
              <div style={{
                fontFamily: 'IBM Plex Sans, sans-serif',
                fontSize: '13px',
                color: COLORS.muted
              }}>
                Automatic PR comments
              </div>
            </div>

            {/* Speed Card */}
            <div style={{
              backgroundColor: '#FFFFFF',
              border: `1px solid ${COLORS.border}`,
              borderRadius: '12px',
              padding: '32px',
              textAlign: 'center',
              opacity: isVisible ? 1 : 0,
              transform: isVisible ? 'translateY(0)' : 'translateY(30px)',
              transition: 'all 0.6s ease-out 0.4s'
            }}>
              <div style={{
                width: '60px',
                height: '60px',
                margin: '0 auto 16px',
                position: 'relative'
              }}>
                <svg width="60" height="60" viewBox="0 0 60 60">
                  <circle
                    cx="30"
                    cy="30"
                    r="25"
                    fill="none"
                    stroke={COLORS.panelLight}
                    strokeWidth="4"
                  />
                  <path
                    d="M 30 30 L 30 10"
                    stroke={COLORS.ink}
                    strokeWidth="3"
                    strokeLinecap="round"
                    style={{
                      transformOrigin: '30px 30px',
                      animation: isVisible ? 'rotateClock 2s ease-out' : 'none'
                    }}
                  />
                </svg>
              </div>
              <div style={{
                fontFamily: 'Space Grotesk, sans-serif',
                fontSize: '36px',
                fontWeight: 700,
                color: COLORS.ink,
                marginBottom: '8px'
              }}>
                30s
              </div>
              <div style={{
                fontFamily: 'IBM Plex Sans, sans-serif',
                fontSize: '14px',
                color: COLORS.muted
              }}>
                Average analysis time
              </div>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes fadeInCode {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes blink {
          0%, 50% {
            opacity: 1;
          }
          51%, 100% {
            opacity: 0;
          }
        }

        @keyframes rotateClock {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(270deg);
          }
        }

        @media (max-width: 1024px) {
          .modern-teams-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </section>
  );
};

