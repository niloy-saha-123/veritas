# GitHub OAuth Setup Guide

## Overview

Veritas.dev uses GitHub OAuth for authentication and stores encrypted fine-grained tokens for automatic issue creation.

## Setup Steps

### 1. Create GitHub OAuth App

1. Go to GitHub → Settings → Developer settings → OAuth Apps
2. Click "New OAuth App"
3. Fill in:
   - **Application name**: Veritas.dev
   - **Homepage URL**: `http://localhost:5173` (or your frontend URL)
   - **Authorization callback URL**: `http://localhost:8000/api/v1/auth/github/callback`
4. Click "Register application"
5. Copy the **Client ID** and generate a **Client Secret**

### 2. Generate Encryption Key

Generate a Fernet encryption key for token storage:

```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())
```

### 3. Update .env File

Add to `backend/.env`:

```bash
# GitHub OAuth
GITHUB_CLIENT_ID=your_client_id_here
GITHUB_CLIENT_SECRET=your_client_secret_here

# Encryption (for token storage)
ENCRYPTION_KEY=your_fernet_key_here

# Database (optional, defaults to SQLite)
DATABASE_URL=sqlite:///./veritas.db
```

### 4. Initialize Database

Run once to create database tables:

```bash
cd backend
python init_db.py
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Start Backend

```bash
python -m uvicorn app.main:app --reload
```

## User Flow

1. User clicks "Sign in with GitHub"
2. Redirected to GitHub OAuth
3. User authorizes the app
4. Callback creates/updates user in database
5. User is redirected to frontend with token form
6. User enters fine-grained token and repo URL
7. Token is encrypted and stored in database
8. Future analyses use stored token automatically

## Fine-Grained Token Requirements

Users need to create a fine-grained token with:
- **Repository access**: Specific repository or all repositories
- **Permissions**: 
  - **Issues**: Read and write

Create at: https://github.com/settings/tokens?type=beta

## Security Notes

- Tokens are encrypted using Fernet (symmetric encryption)
- Encryption key should be kept secret in `.env`
- Never commit `.env` file to version control
- In production, use environment variables or secret management
