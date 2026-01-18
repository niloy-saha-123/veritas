import React from 'react';
import { COLORS } from './constants/constants';
import { Header } from './components/Header';
import { Hero } from './components/Hero';
import { WorkflowDiagram } from './components/WorkflowDiagram';
import { ProductIntro } from './components/ProductIntro';
import { ModernTeamsSection } from './components/ModernTeamsSection';
import { TrustScoreChart } from './components/TrustScoreChart';
import { SplitSection } from './components/SplitSection';
import { LiveExample } from './components/LiveExample';
import { PricingSection } from './components/PricingSection';
import { Footer } from './components/Footer';

// Main App Component
export default function App() {
  return (
    <div style={{
      fontFamily: 'IBM Plex Sans, sans-serif',
      backgroundColor: COLORS.canvas,
      minHeight: '100vh',
      position: 'relative'
    }}>
      {/* Fixed Grid Background */}
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        backgroundImage: `
          linear-gradient(rgba(91, 95, 106, 0.2) 1px, transparent 1px),
          linear-gradient(90deg, rgba(91, 95, 106, 0.2) 1px, transparent 1px)
        `,
        backgroundSize: '32px 32px',
        pointerEvents: 'none',
        zIndex: 0
      }} />

      {/* Gradient Overlays */}
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        background: `
          radial-gradient(circle 1000px at 20% 20%, rgba(0, 217, 255, 0.08), transparent),
          radial-gradient(circle 900px at 80% 80%, rgba(255, 107, 53, 0.06), transparent),
          radial-gradient(circle 700px at 50% 50%, rgba(255, 230, 109, 0.04), transparent)
        `,
        pointerEvents: 'none',
        zIndex: 0
      }} />

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700;800&family=IBM Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
        
        * {
          box-sizing: border-box;
        }
        
        body {
          margin: 0;
          padding: 0;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
        
        @media (prefers-reduced-motion: reduce) {
          * {
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
          }
        }
      `}</style>

      <div style={{ position: 'relative', zIndex: 1 }}>
        <Header />
        <Hero />
        <WorkflowDiagram />
        <ProductIntro />
        <ModernTeamsSection />
        <TrustScoreChart />
        <SplitSection />
        <LiveExample />
        <PricingSection />
        <Footer />
      </div>
    </div>
  );
}

