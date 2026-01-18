import React, { useState, useEffect, useRef } from 'react';
import { COLORS } from '../constants/constants';

// Trust Score Over Time Chart
export const TrustScoreChart = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [animatedPoints, setAnimatedPoints] = useState([]);
  const sectionRef = useRef(null);

  const points = [
    { week: 'Week 1', score: 65, x: 60, y: 190 },
    { week: 'Week 2', score: 75, x: 200, y: 175 },
    { week: 'Week 3', score: 85, x: 340, y: 145 },
    { week: 'Week 4', score: 92, x: 480, y: 120 }
  ];

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          // Animate points sequentially
          points.forEach((point, idx) => {
            setTimeout(() => {
              setAnimatedPoints(prev => [...prev, point]);
            }, idx * 300);
          });
        }
      },
      { threshold: 0.5 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <section ref={sectionRef} style={{
      padding: '64px 32px',
      backgroundColor: COLORS.canvas
    }}>
      <div style={{
        maxWidth: '600px',
        margin: '0 auto',
        backgroundColor: '#FFFFFF',
        border: `1px solid ${COLORS.border}`,
        borderRadius: '12px',
        padding: '40px',
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'scale(1)' : 'scale(0.95)',
        transition: 'all 0.6s ease-out'
      }}>
        <h3 style={{
          fontFamily: 'IBM Plex Sans, sans-serif',
          fontSize: '18px',
          fontWeight: 600,
          color: COLORS.ink,
          margin: '0 0 32px 0'
        }}>
          Trust Score Over Time
        </h3>

        <svg width="100%" height="250" viewBox="0 0 540 250" style={{ overflow: 'visible' }}>
          {/* Grid lines */}
          <line x1="60" y1="200" x2="480" y2="200" stroke={COLORS.border} strokeWidth="1" />
          
          {/* Animated line */}
          {animatedPoints.length > 1 && (
            <path
              d={`M ${animatedPoints.map(p => `${p.x},${p.y}`).join(' L ')}`}
              fill="none"
              stroke={COLORS.ink}
              strokeWidth="3"
              style={{
                strokeDasharray: 1000,
                strokeDashoffset: isVisible ? 0 : 1000,
                transition: 'stroke-dashoffset 1.5s ease-out'
              }}
            />
          )}

          {/* Animated points */}
          {animatedPoints.map((point, idx) => (
            <g key={idx}>
              <circle
                cx={point.x}
                cy={point.y}
                r="6"
                fill={COLORS.ink}
                style={{
                  animation: 'popIn 0.3s ease-out',
                  transformOrigin: `${point.x}px ${point.y}px`
                }}
              />
              <circle
                cx={point.x}
                cy={point.y}
                r="10"
                fill="none"
                stroke={COLORS.ink}
                strokeWidth="2"
                opacity="0"
                style={{
                  animation: 'ripple 1s ease-out infinite',
                  animationDelay: `${idx * 0.3}s`
                }}
              />
            </g>
          ))}

          {/* Labels */}
          <text x="60" y="225" fontSize="13" fill={COLORS.muted} fontFamily="IBM Plex Sans">Week 1</text>
          <text x="460" y="225" fontSize="13" fill={COLORS.muted} fontFamily="IBM Plex Sans">Week 4</text>
        </svg>
      </div>

      <style>{`
        @keyframes popIn {
          0% {
            transform: scale(0);
            opacity: 0;
          }
          50% {
            transform: scale(1.2);
          }
          100% {
            transform: scale(1);
            opacity: 1;
          }
        }

        @keyframes ripple {
          0% {
            r: 6;
            opacity: 0.5;
          }
          100% {
            r: 20;
            opacity: 0;
          }
        }
      `}</style>
    </section>
  );
};

