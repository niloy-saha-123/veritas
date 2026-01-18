import { useState } from 'react'
import { useFadeIn } from '../hooks/useFadeIn'
import './BuiltForTeams.css'

function BuiltForTeams() {
  const [ref, isVisible] = useFadeIn({ threshold: 0.1 })
  const [selectedLanguage, setSelectedLanguage] = useState('Java')
  const [activeFile, setActiveFile] = useState('Main.java')

  const codeExamples = {
    Python: {
      files: {
        'auth.py': `def authenticate_user(email, password):
    """Authenticate a user with email and password.
    
    Args:
        email: User email address
        password: User password
    
    Returns:
        User object or None if invalid credentials
    """
    user = get_user_by_email(email)
    if user and verify_password(user, password):
        return user
    return None`,
        'validator.py': `def validate_payment(amount, currency):
    """Validate payment parameters.
    
    Args:
        amount: Payment amount
        currency: Currency code
    
    Returns:
        bool: True if valid, False otherwise
    """
    if amount <= 0:
        return False
    valid_currencies = ['USD', 'EUR', 'GBP']
    return currency in valid_currencies`,
        'main.py': `def process_payment(amount, currency):
    """Process a payment transaction.
    
    Args:
        amount: Payment amount in cents
        currency: Currency code (e.g., 'USD', 'EUR')
    
    Returns:
        Transaction ID or None if invalid
    """
    if amount <= 0:
        return None
    return payment_gateway.charge(amount, currency)`
      }
    },
    TypeScript: {
      files: {
        'payment.ts': `interface PaymentRequest {
  amount: number;
  currency: string;
}

function createPayment(request: PaymentRequest): string {
  return paymentService.initialize(request);
}`,
        'processor.ts': `class PaymentProcessor {
  private gateway: PaymentGateway;

  constructor(gateway: PaymentGateway) {
    this.gateway = gateway;
  }

  process(amount: number): string {
    return this.gateway.charge(amount);
  }
}`,
        'main.ts': `function processPayment(
  amount: number,
  currency: string
): string | null {
  /**
   * Process a payment transaction.
   * @param amount - Payment amount in cents
   * @param currency - Currency code (e.g., 'USD', 'EUR')
   * @returns Transaction ID or null if invalid
   */
  if (amount <= 0) return null;
  return paymentGateway.charge(amount, currency);
}`
      }
    },
    Java: {
      files: {
        'Payment.java': `public class Payment {
  private int amount;
  private String currency;

  public Payment(int amount, String currency) {
    this.amount = amount;
    this.currency = currency;
  }

  public int getAmount() {
    return amount;
  }
}`,
        'Processor.java': `public class Processor {
  public void processPayment(Payment payment) {
    // Process payment logic
    validatePayment(payment);
    executePayment(payment);
  }
}`,
        'Main.java': `public class PaymentProcessor {
  /**
   * Process a payment transaction.
   * @param amount Payment amount in cents
   * @param currency Currency code (e.g., "USD", "EUR")
   * @return Transaction ID or null if invalid
   */
  public String processPayment(int amount, String currency) {
    if (amount <= 0) return null;
    return paymentGateway.charge(amount, currency);
  }
}`
      }
    },
    JSON: {
      files: {
        'config.json': `{
  "app": {
    "name": "Payment Service",
    "version": "1.0.0",
    "port": 3000
  },
  "database": {
    "host": "localhost",
    "port": 5432
  }
}`,
        'schema.json': `{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "amount": { "type": "integer" },
    "currency": { "type": "string" }
  },
  "required": ["amount", "currency"]
}`,
        'api.json': `{
  "payment": {
    "process": {
      "method": "POST",
      "path": "/api/payments",
      "parameters": {
        "amount": {
          "type": "integer",
          "description": "Payment amount in cents",
          "required": true
        },
        "currency": {
          "type": "string",
          "description": "Currency code (e.g., 'USD', 'EUR')",
          "required": true
        }
      }
    }
  }
}`
      }
    },
    Markdown: {
      files: {
        'README.md': `# Payment Service

A modern payment processing service built with TypeScript.

## Features

- Secure payment processing
- Multi-currency support
- Real-time transaction tracking

## Installation

\`\`\`bash
npm install
npm start
\`\`\``,
        'API.md': `## processPayment

Process a payment transaction.

### Parameters

- \`amount\` (integer): Payment amount in cents
- \`currency\` (string): Currency code (e.g., 'USD', 'EUR')

### Returns

Transaction ID or null if invalid

### Example

\`\`\`javascript
const result = processPayment(1000, 'USD');
\`\`\``,
        'GUIDE.md': `# Getting Started Guide

## Quick Start

1. Clone the repository
2. Install dependencies
3. Configure your API keys
4. Run the service

## Configuration

Edit \`config.json\` to customize settings.`
      }
    }
  }

  const languages = ['Python', 'TypeScript', 'Java', 'JSON', 'Markdown']
  const currentExample = codeExamples[selectedLanguage]
  const fileList = Object.keys(currentExample.files)
  
  // Reset active file when language changes
  const handleLanguageChange = (lang) => {
    setSelectedLanguage(lang)
    const newFiles = Object.keys(codeExamples[lang].files)
    setActiveFile(newFiles[0])
  }

  // Get the code for the currently active file
  const currentCode = currentExample.files[activeFile] || currentExample.files[fileList[0]]

  return (
    <section 
      ref={ref}
      className={`built-for-teams fade-in-section ${isVisible ? 'is-visible' : ''}`}
    >
      <div className="built-for-teams-container">
        <h2 className="section-main-title">Built for Modern Teams</h2>
        
        <div className="features-layout">
          {/* Left: Multi-Language Support */}
          <div className="multi-language-card">
            <h3 className="card-title">Multi-Language Support</h3>
            
            <div className="language-tabs">
              {languages.map((lang) => (
                <button
                  key={lang}
                  className={`language-tab ${selectedLanguage === lang ? 'active' : ''}`}
                  onClick={() => handleLanguageChange(lang)}
                >
                  {lang}
                </button>
              ))}
            </div>

            <div className="code-editor">
              <div className="file-tabs">
                {fileList.map((file) => (
                  <div
                    key={file}
                    className={`file-tab ${activeFile === file ? 'active' : ''}`}
                    onClick={() => setActiveFile(file)}
                  >
                    {file}
                  </div>
                ))}
              </div>
              <div className="code-content">
                <pre><code className={`language-${selectedLanguage.toLowerCase()}`}>
                  {currentCode}
                </code></pre>
              </div>
            </div>
          </div>

          {/* Right: Feature Cards */}
          <div className="feature-cards">
            <div className="feature-card">
              <div className="trust-score-circle">
                <svg className="score-ring" viewBox="0 0 100 100">
                  <circle
                    className="score-ring-background"
                    cx="50"
                    cy="50"
                    r="45"
                    fill="none"
                    stroke="#e5e5e5"
                    strokeWidth="8"
                  />
                  <circle
                    className="score-ring-progress"
                    cx="50"
                    cy="50"
                    r="45"
                    fill="none"
                    stroke="#1a1a1a"
                    strokeWidth="8"
                    strokeDasharray={`${2 * Math.PI * 45}`}
                    strokeDashoffset={`${2 * Math.PI * 45 * (1 - 0.92)}`}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="score-value">92%</div>
              </div>
              <p className="feature-label">Trust Score</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon github-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 2C6.48 2 2 6.48 2 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.08 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12c0-5.52-4.48-10-10-10z"/>
                </svg>
              </div>
              <h4 className="feature-title">GitHub App Integration</h4>
              <p className="feature-subtitle">Automatic issue creation</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon time-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12 6 12 12 16 14"/>
                </svg>
              </div>
              <div className="time-value">30s</div>
              <p className="feature-subtitle">Average analysis time</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default BuiltForTeams
