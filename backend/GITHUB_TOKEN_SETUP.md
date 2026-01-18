# GitHub Token Setup Guide for PR Creation

## Error: "Resource not accessible by personal access token"

This error means your GitHub token doesn't have the required permissions to create PRs in the repository.

## Solution: Create a Token with Correct Permissions

### Step 1: Create a Classic Personal Access Token

1. **Go to GitHub Settings:**
   - Visit: https://github.com/settings/tokens
   - Or: GitHub → Your Profile → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Generate New Token:**
   - Click "Generate new token" → "Generate new token (classic)"
   - **Note:** Use **Classic** token, not fine-grained (fine-grained tokens have different permissions)

3. **Configure Token:**
   - **Note:** Give it a name like "Veritas.dev PR Creation"
   - **Expiration:** Choose 30, 60, 90 days, or No expiration
   - **Select scopes:** ⚠️ **CRITICAL** - Check the following:

### Required Scopes:

✅ **repo** (Full control of private repositories)
   - This includes ALL of these:
   - ✅ repo:status
   - ✅ repo_deployment
   - ✅ public_repo
   - ✅ repo:invite
   - ✅ security_events

**For Organization Repositories:**

If the repository is in an organization, you may ALSO need:

4. **Organization Approval:**
   - Some organizations require approval for tokens with `repo` scope
   - Your organization admin must approve the token

5. **SSO Authorization (if required):**
   - After generating the token, look for "Configure SSO" next to it
   - Click "Configure SSO" and authorize it for your organization
   - This is REQUIRED if your organization uses SSO

### Step 2: Copy and Save Token

1. **Copy the token immediately** (you can't see it again!)
2. It will look like: `github_pat_11A2VOA3Q0YordchalRxmv...`

### Step 3: Update Your .env File

Open `backend/.env` and add/update:

```bash
GITHUB_TOKEN=your_new_token_here
```

**Important:** Replace `your_new_token_here` with your actual token.

### Step 4: Restart Backend Server

```bash
# Stop current server (Ctrl+C)
# Then restart:
cd backend
python -m uvicorn app.main:app --reload
```

## Verification: Test Your Token

You can test if your token works by running:

```bash
# Replace YOUR_TOKEN with your actual token
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
```

If this returns your GitHub user info, the token is valid.

Test repository access:

```bash
# Replace OWNER, REPO, and YOUR_TOKEN
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/repos/OWNER/REPO
```

If this returns repository details, you have access. If it returns 404/403, the token lacks permissions.

## Common Issues

### Issue 1: "Resource not accessible by personal access token"

**Cause:** Token doesn't have `repo` scope or organization SSO not authorized.

**Fix:** 
- Ensure `repo` scope is selected
- If organization repo: authorize SSO for the token

### Issue 2: Fine-Grained vs Classic Token

**Classic tokens** (recommended for this use case):
- Simpler permission model
- Can select entire "repo" scope
- Location: Personal access tokens → Tokens (classic)

**Fine-grained tokens:**
- More granular permissions
- May require different setup
- Not recommended for this use case

**Fix:** Use **Classic** token, not fine-grained.

### Issue 3: Organization SSO Required

**Symptom:** Token works for personal repos but fails for organization repos.

**Fix:**
1. After creating token, find it in your token list
2. Click "Configure SSO" next to the token
3. Authorize it for your organization
4. You'll see a green checkmark when authorized

### Issue 4: Repository is Private

**For private repositories:** You MUST have the full `repo` scope, not just `public_repo`.

**Fix:** Select the full `repo` scope checkbox.

## Quick Reference

- **Token Creation:** https://github.com/settings/tokens
- **Required Scope:** `repo` (full control)
- **Token Type:** Classic (not fine-grained)
- **For Organizations:** May need SSO authorization
- **For Private Repos:** Must have `repo` scope

## Still Having Issues?

1. Verify token has `repo` scope
2. Check if repository is in an organization requiring SSO
3. Test token with curl commands above
4. Check backend logs for detailed error messages
5. Ensure `.env` file is loaded (restart server after updating)
