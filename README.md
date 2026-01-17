<<<<<<< HEAD
# veritas
=======
# Veritas.dev

---

## 🏗️ Project Structure

```
nexhacks/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── api/               # API routes
│   │   │   └── routes/
│   │   │       ├── health.py  # Health check endpoints
│   │   │       └── analysis.py # Analysis endpoints
│   │   ├── core/              # Core functionality
│   │   │   ├── config.py      # Configuration management
│   │   │   └── detection_engine.py # Discrepancy detection
│   │   ├── services/          # Business logic
│   │   │   ├── code_parser.py # Code parsing service
│   │   │   ├── doc_parser.py  # Documentation parsing
│   │   │   ├── comparator.py  # Comparison logic
│   │   │   └── integrations/  # Sponsor API integrations
│   │   │       ├── token_company.py
│   │   │       ├── devswarm.py
│   │   │       └── arize.py
│   │   ├── models/            # Data models
│   │   │   └── schemas.py     # Pydantic schemas
│   │   └── utils/             # Utilities
│   │       └── helpers.py
│   ├── tests/                 # Test suite
│   │   ├── test_parser.py
│   │   └── test_comparator.py
│   ├── requirements.txt       # Python dependencies
│   └── .env.example          # Environment template
│
├── frontend/                  # React Frontend
│   ├── public/
│   └── src/
│       ├── components/
│       ├── pages/
│       └── App.jsx
│
├── browser-extension/         # Chrome/Firefox Extension
│   ├── manifest.json         # Extension configuration
│   ├── popup/                # Extension popup UI
│   │   ├── popup.html
│   │   └── popup.js
│   ├── content/              # Content scripts
│   │   └── content.js
│   ├── background/           # Background service worker
│   │   └── background.js
│   └── assets/               # Icons and images
│
├── github-action/            # GitHub Action
│   ├── action.yml           # Action configuration
│   └── src/
│       └── index.js         # Action implementation
│
├── docs/                    # Project documentation
│   └── api-documentation.md
│
├── .gitignore
└── README.md
```

---

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Web framework
- **Pydantic** - Data validation
- **Python AST** - Code parsing
- **Uvicorn** - ASGI server

### Frontend
- **React** - UI framework
- **Vite** - Build tool

### Browser Extension
- **Vanilla JavaScript**
- **Chrome Extension API v3**

### Integrations
- Token Company
- DevSwarm
- Arize
- LeanMCP

---

## 🚀 Setup & Commands

### Backend

```bash
# Navigate to project
cd /Users/niloysaha/IdeaProjects/veritas/nexhacks

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment (optional)
cp backend/.env.example backend/.env

# Run server
cd backend
python -m uvicorn app.main:app --reload
```

### Endpoints

- Root: http://localhost:8000
- Health: http://localhost:8000/api/v1/health
- Status: http://localhost:8000/api/v1/status
- Docs: http://localhost:8000/api/docs

### Testing

```bash
cd backend
pytest tests/ -v
```

### Browser Extension

1. Open `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select `browser-extension` directory

### GitHub Action

```yaml
- uses: ./github-action
  with:
    code-path: './src'
    docs-path: './docs'
    language: 'python'
```

---

## 📡 API Examples

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Analyze
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "code_content": "def hello():\n    pass",
    "doc_content": "# hello()\nSays hello",
    "language": "python"
  }'
```

---

**NexHacks**
>>>>>>> 1cae8de6781e5207cb454ff0ad898dcc7c2cc3d3
