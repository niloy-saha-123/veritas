# Veritas GitHub App Setup Guide

This guide walks you through setting up the Veritas documentation verification agent as a GitHub App.

## What You Need

| Credential | Required | Where to Get |
|-----------|----------|--------------|
| `GITHUB_APP_ID` | ✅ Yes | GitHub Developer Settings |
| `GITHUB_PRIVATE_KEY` | ✅ Yes | Generated when creating GitHub App |
| `GITHUB_WEBHOOK_SECRET` | ✅ Yes | You create this (random string) |
| `GEMINI_API_KEY` | ✅ Yes | Google AI Studio |
| `TOKEN_COMPANY_API_KEY` | ⚪ Optional | Token Company (for compression) |

---

## Step 1: Create a GitHub App

### 1.1 Go to GitHub Developer Settings

1. Go to [github.com/settings/apps](https://github.com/settings/apps)
2. Click **"New GitHub App"**

### 1.2 Fill in Basic Information

| Field | Value |
|-------|-------|
| **GitHub App name** | `Veritas Docs Bot` (or your preferred name) |
| **Homepage URL** | `https://veritas.dev` (or your domain) |
| **Webhook URL** | `https://your-server.com/github/webhook` |
| **Webhook secret** | Generate a random string (save this!) |

**To generate a webhook secret:**
```bash
openssl rand -hex 32
```

### 1.3 Set Permissions

Under **"Permissions"**, set:

| Permission | Access Level | Why |
|------------|--------------|-----|
| **Contents** | Read & Write | To read code and create doc files |
| **Pull requests** | Read & Write | To read PR changes |
| **Issues** | Read & Write | To create issues for mismatches |
| **Commit statuses** | Read & Write | To show "Veritas is checking..." |
| **Metadata** | Read-only | Required for all apps |

### 1.4 Subscribe to Events

Check these boxes under **"Subscribe to events"**:

- ✅ **Pull request**
- ✅ **Push** (optional, for future features)

### 1.5 Where can this GitHub App be installed?

Select: **"Any account"** (or "Only on this account" for private use)

### 1.6 Create the App

Click **"Create GitHub App"**

---

## Step 2: Get Your Credentials

### 2.1 Get App ID

After creating the app, you'll see your **App ID** at the top of the page.
It's a number like `123456`.

### 2.2 Generate Private Key

1. Scroll down to **"Private keys"**
2. Click **"Generate a private key"**
3. A `.pem` file will download
4. Keep this file safe!

### 2.3 Format the Private Key for .env

The private key needs to be in a single line with `\n` for newlines.

**Option A: Manual conversion**
```bash
# On Mac/Linux
awk 'NF {sub(/\r/, ""); printf "%s\\n",$0;}' your-app-name.pem
```

**Option B: Use the file path**
You can also store the path to the file and load it differently.

---

## Step 3: Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click **"Create API Key"**
3. Copy the key

---

## Step 4: Configure Environment

### 4.1 Create .env file

```bash
cd backend
cp .env.example .env
```

### 4.2 Fill in your credentials

Edit `.env`:

```env
# GitHub App Configuration
GITHUB_APP_ID=123456
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\nMIIE...(your key here)...\n-----END RSA PRIVATE KEY-----"
GITHUB_WEBHOOK_SECRET=your-webhook-secret-from-step-1

# Gemini API Key
GEMINI_API_KEY=your-gemini-api-key

# Server Configuration
API_PORT=8000
API_HOST=0.0.0.0
DEBUG=True
```

---

## Step 5: Deploy Your Server

### Option A: Local Testing with ngrok

```bash
# Terminal 1: Start the server
cd backend
pip install -r requirements.txt
python main.py

# Terminal 2: Expose via ngrok
ngrok http 8000
```

Copy the ngrok URL (e.g., `https://abc123.ngrok.io`) and update your GitHub App's webhook URL to:
```
https://abc123.ngrok.io/github/webhook
```

### Option B: Deploy to Vercel

Your project already has `vercel.json` configured:

```bash
cd backend
vercel --prod
```

Update your GitHub App's webhook URL to your Vercel URL.

### Option C: Deploy to Railway/Render

1. Connect your GitHub repo
2. Set environment variables in the dashboard
3. Deploy

---

## Step 6: Install the App

1. Go to your GitHub App's page
2. Click **"Install App"**
3. Choose which repositories to install on
4. Click **"Install"**

---

## Step 7: Test It!

1. Create a new branch in an installed repository
2. Add a new function without documentation:

```python
# test_file.py
def calculate_discount(price, percentage):
    return price * (1 - percentage / 100)
```

3. Create a Pull Request
4. Watch Veritas:
   - Sets status to "pending"
   - Analyzes the code
   - Creates a documentation PR (since no docs exist)
   - Sets status to "success"

---

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                     PR Created/Updated                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 GitHub sends webhook                         │
│                 POST /github/webhook                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Set status: "Veritas is analyzing..."          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Parse changed code files                        │
│              Get existing documentation                      │
│              Compare using AI                                │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ No docs found   │ │ Docs mismatch   │ │ Everything OK   │
│                 │ │                 │ │                 │
│ → Create PR     │ │ → Create Issue  │ │ → Success ✓     │
│   with docs     │ │   with details  │ │                 │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

---

## Troubleshooting

### "Invalid webhook signature"

- Check that `GITHUB_WEBHOOK_SECRET` in your `.env` matches the secret in GitHub App settings
- Make sure there are no extra spaces or quotes

### "Failed to get installation token"

- Check that `GITHUB_APP_ID` is correct
- Check that `GITHUB_PRIVATE_KEY` is properly formatted with `\n`
- Make sure the app is installed on the repository

### "GEMINI_API_KEY is not set"

- Add your Gemini API key to `.env`
- Restart the server

### Webhook not firing

- Check GitHub App settings → "Advanced" → "Recent Deliveries"
- Make sure webhook URL is correct and accessible
- Verify the app is installed on the repository

---

## Files Modified

| File | Changes |
|------|---------|
| `app/core/config.py` | Added GitHub App settings |
| `app/github/auth.py` | Added commit status, file operations |
| `app/github/webhook_handler.py` | Complete rewrite with proper flow |
| `app/github/doc_generator.py` | New file: AI documentation generator |
| `main.py` | Updated with proper error handling |
| `.env.example` | Updated with all required variables |

---

## Support

If you encounter issues:
1. Check the server logs for error messages
2. Check GitHub App → Advanced → Recent Deliveries for webhook status
3. Verify all environment variables are set correctly

---

*Built with ❤️ by Veritas*
