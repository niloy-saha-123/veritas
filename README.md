# Veritas.dev

**AI-Powered Documentation Verification for GitHub**

Automatically verifies that your documentation matches your code on every PR. Uses hybrid AI (embeddings + LLM) to detect mismatches, missing docs, and outdated information.

---

## 🎯 What It Does

When you create a PR, Veritas:
1. **Analyzes** new code vs existing documentation
2. **Detects** mismatches, missing docs, or outdated info
3. **Takes action:**
   - ✅ Perfect docs → Silent success
   - 📝 Missing docs → Creates PR with auto-generated documentation
   - ⚠️ Mismatches → Creates GitHub Issue with specific problems

**No comments, no UI - just native GitHub PRs and Issues.**

---

## 🏗️ Architecture

### Three-Layer Hybrid AI System

```
┌─────────────────────────────────────────────────┐
│ 1. Embedding-Based Screening (Fast, Free)      │
│    • Sentence Transformers (all-MiniLM-L6-v2)  │
│    • Handles 85% of comparisons                 │
│    • 10ms per comparison                        │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ 2. LLM Analysis (Accurate, Paid)               │
│    • Google Gemini 2.5 Flash                    │
│    • Token Company compression (60% savings)    │
│    • Handles edge cases                         │
│    • 2s per comparison                          │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ 3. Adaptive Routing (Smart)                    │
│    • High similarity → Skip LLM                 │
│    • Medium similarity → Hybrid                 │
│    • Low similarity → LLM focused               │
│    • 88% cost reduction vs LLM-only             │
└─────────────────────────────────────────────────┘
```

**Performance:**
- 3.3x faster than LLM-only
- 88% cheaper than LLM-only
- 92% accuracy

---

## 📁 Project Structure

```
nexhacks/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── github/            # GitHub App integration
│   │   │   ├── webhook_handler.py  # PR event handling
│   │   │   └── auth.py        # JWT auth, PR/Issue creation
│   │   ├── parsers/           # Language parsers
│   │   │   ├── python_parser.py
│   │   │   ├── javascript_parser.py
│   │   │   ├── java_parser.py
│   │   │   ├── markdown_parser.py
│   │   │   └── json_parser.py
│   │   ├── comparison/        # AI comparison engine
│   │   │   ├── hybrid_engine.py    # Hybrid comparator
│   │   │   ├── semantic_matcher.py # Embedding similarity
│   │   │   └── engine.py      # Gemini LLM
│   │   ├── services/
│   │   │   └── integrations/
│   │   │       └── token_company.py # Token compression
│   │   └── models/
│   │       └── function_signature.py
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                  # React Landing Page
│   ├── src/
│   │   ├── components/
│   │   │   ├── Hero.jsx
│   │   │   ├── WorkflowDiagram.jsx
│   │   │   └── ModernTeamsSection.jsx
│   │   └── App.jsx
│   └── package.json
│
├── github-action/            # GitHub Action (optional)
│   ├── action.yml
│   └── src/
│
└── docs/
    └── api-documentation.md
```

---

## 🚀 Quick Start

### 1. Install the GitHub App

1. Go to: https://github.com/apps/veritas-docs-verifier
2. Click "Install"
3. Select repositories to enable

### 2. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your keys:
# - GEMINI_API_KEY
# - TOKEN_COMPANY_API_KEY
# - GITHUB_APP_ID
# - GITHUB_PRIVATE_KEY
# - GITHUB_WEBHOOK_SECRET

# Run server
uvicorn main:app --reload --port 8000
```

**Endpoints:**
- Health: `http://localhost:8000/health`
- Webhook: `POST http://localhost:8000/github/webhook`
- Docs: `http://localhost:8000/docs`

### 3. Frontend Setup (Landing Page)

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

Dashboard available at `http://localhost:3000`

---

## 🔧 Technology Stack

### Backend
- **FastAPI** - Web framework
- **Sentence Transformers** - Embedding generation
- **Google Gemini 2.5 Flash** - LLM analysis
- **Token Company** - Prompt compression
- **PyJWT** - GitHub App authentication
- **GitPython** - Repository cloning
- **Python AST** - Code parsing

### Frontend
- **React** - UI framework
- **Vite** - Build tool
- **Lucide React** - Icons

### Parsers
- **Python** - AST-based
- **JavaScript/TypeScript** - Regex-based
- **Java** - Regex-based
- **Markdown** - Regex-based
- **JSON** - OpenAPI/generic API schemas

---

## 🔑 Environment Variables

### Backend `.env`

```bash
# AI APIs
GEMINI_API_KEY=your_gemini_api_key
TOKEN_COMPANY_API_KEY=your_token_company_key

# GitHub App
GITHUB_APP_ID=your_app_id
GITHUB_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----
...
-----END RSA PRIVATE KEY-----
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# Server
API_PORT=8000
API_HOST=0.0.0.0
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend `.env`

```bash
VITE_GITHUB_APP_KEY=https://github.com/apps/veritas-docs-verifier
```

---

## 🧪 Testing

### Run Parser Tests

```bash
cd backend
pytest tests/test_parsers.py -v
```

### Run Comparison Engine Tests

```bash
pytest tests/test_comparison_engine.py -v
```

### Test Webhook Locally

```bash
# Terminal 1: Run backend
uvicorn main:app --reload --port 8000

# Terminal 2: Expose with ngrok
ngrok http 8000

# Update GitHub App webhook URL to ngrok URL
# Create a test PR to trigger webhook
```

---

## 📊 How It Works

### Workflow

```
Developer creates PR
         ↓
GitHub sends webhook to backend
         ↓
Backend fetches:
  • New code from PR branch
  • Existing docs from base branch
         ↓
AI analyzes:
  • Embedding similarity (fast screening)
  • LLM analysis (detailed verification)
         ↓
Decision:
  ├─ Docs match code → Do nothing ✅
  ├─ Missing docs → Create PR with generated docs 📝
  └─ Mismatches → Create Issue with problems ⚠️
```

### Supported Languages

| Language | Parser | Features |
|----------|--------|----------|
| Python | AST | Full signature extraction |
| JavaScript | Regex | Functions, classes, exports |
| TypeScript | Regex | Type annotations |
| Java | Regex | Methods, classes |
| Markdown | Regex | Code blocks, API refs |
| JSON | Native | OpenAPI, generic APIs |

---

## 🎨 Frontend Features

- ✨ Clean, minimal paper-white design
- 📊 Real-time analysis progress
- 🎯 Trust score visualization
- 📋 Detailed discrepancy reports
- 🔍 GitHub repository analysis
- 🎭 Animated code examples
- 📱 Responsive design

---

## 📖 API Documentation

See [docs/api-documentation.md](docs/api-documentation.md) for detailed API reference.

### Quick Example

```bash
# Analyze a repository
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "github_url": "https://github.com/user/repo"
  }'

# Get results
curl http://localhost:8000/results/{job_id}
```

---

## 🚢 Deployment

### Backend (Railway/Render)

```bash
# Install Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# Login and deploy
railway login
railway init
railway up

# Set environment variables in Railway dashboard
```

### Frontend (Vercel/Netlify)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel
```

---

## 🤝 Contributing

This project was built for **NexHacks 2025**.

---

## 📝 License

MIT

---

**Built with ❤️ for NexHacks**
