# Deployment Guide - Render

This guide covers deploying the AI Lead Qualification Agent to Render.

## Prerequisites

- GitHub account
- Render account (free tier available at https://render.com)
- Code pushed to a GitHub repository

## Architecture on Render

```
┌──────────────────┐
│  Web Service     │  <- FastAPI Backend
│  (Python)        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  PostgreSQL      │  <- Managed Database
│  Database        │
└──────────────────┘

┌──────────────────┐
│  Static Site     │  <- React Frontend
│  (Node.js)       │
└──────────────────┘
```

## Step 1: Prepare Repository

### 1.1 Backend Preparation

Ensure you have these files in your repository:

**`backend/requirements.txt`** - Already created ✓

**`render.yaml`** (Create at repository root):

```yaml
services:
  # Backend Web Service
  - type: web
    name: lead-qualification-api
    env: python
    region: oregon
    plan: free
    buildCommand: cd backend && pip install -r requirements.txt
    startCommand: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DATABASE_URL
        fromDatabase:
          name: lead-qualification-db
          property: connectionString
      - key: OPENAI_API_KEY
        sync: false
      - key: SENDGRID_API_KEY
        sync: false
      - key: TWILIO_ACCOUNT_SID
        sync: false
      - key: TWILIO_AUTH_TOKEN
        sync: false
      - key: CALENDLY_API_KEY
        sync: false
      - key: HUBSPOT_API_KEY
        sync: false

  # Frontend Static Site
  - type: web
    name: lead-qualification-frontend
    env: static
    region: oregon
    buildCommand: cd frontend && npm install && npm run build
    staticPublishPath: frontend/dist
    envVars:
      - key: VITE_API_URL
        value: https://lead-qualification-api.onrender.com

databases:
  # PostgreSQL Database
  - name: lead-qualification-db
    plan: free
    region: oregon
```

### 1.2 Add Procfile for Backend

Create `backend/Procfile`:

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 1.3 Update Backend for Production

Ensure `backend/config.py` reads PORT from environment:

```python
PORT: int = int(os.getenv("PORT", 8000))
```

## Step 2: Deploy to Render

### Method 1: Using render.yaml (Recommended)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

2. **Connect to Render**:
   - Go to https://dashboard.render.com
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Select the repository
   - Render will automatically detect `render.yaml`

3. **Configure Environment Variables**:
   - Go to each service in Render dashboard
   - Navigate to "Environment" tab
   - Add required variables:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `SENDGRID_API_KEY`: (Optional)
     - `TWILIO_ACCOUNT_SID`: (Optional)
     - `TWILIO_AUTH_TOKEN`: (Optional)
     - `CALENDLY_API_KEY`: (Optional)
     - `HUBSPOT_API_KEY`: (Optional)

4. **Deploy**:
   - Click "Apply" to start deployment
   - Wait for services to build and deploy (5-10 minutes)

### Method 2: Manual Deployment

#### Deploy Backend:

1. **Create Web Service**:
   - Go to Render Dashboard
   - Click "New" → "Web Service"
   - Connect GitHub repository
   - Configure:
     - Name: `lead-qualification-api`
     - Environment: `Python 3`
     - Region: `Oregon (US West)`
     - Branch: `main`
     - Root Directory: `backend`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

2. **Create Database**:
   - Click "New" → "PostgreSQL"
   - Name: `lead-qualification-db`
   - Plan: `Free`
   - Region: `Oregon (US West)`

3. **Connect Database**:
   - Go to backend service
   - Environment tab
   - Add `DATABASE_URL` from database's Internal Connection String

4. **Add Environment Variables**:
   - `OPENAI_API_KEY`: Your OpenAI key
   - Other API keys as needed

#### Deploy Frontend:

1. **Create Static Site**:
   - Click "New" → "Static Site"
   - Connect repository
   - Configure:
     - Name: `lead-qualification-frontend`
     - Root Directory: `frontend`
     - Build Command: `npm install && npm run build`
     - Publish Directory: `dist`

2. **Add Environment Variable**:
   - `VITE_API_URL`: Your backend URL (e.g., `https://lead-qualification-api.onrender.com`)

## Step 3: Post-Deployment Setup

### 3.1 Initialize Database

After first deployment, initialize the database:

1. Go to backend service
2. Click "Shell" tab
3. Run:
   ```bash
   python -c "from database import init_db; init_db()"
   ```

### 3.2 Update CORS Settings

Update `backend/config.py` to include your frontend URL:

```python
CORS_ORIGINS = "https://lead-qualification-frontend.onrender.com,http://localhost:3000"
```

Commit and push to redeploy.

### 3.3 Test Deployment

1. **Backend Health Check**:
   ```bash
   curl https://lead-qualification-api.onrender.com/health
   ```

2. **Frontend Access**:
   - Visit your frontend URL
   - Create a test lead
   - Verify processing works

## Step 4: Custom Domain (Optional)

### Backend Domain:

1. Go to backend service settings
2. Click "Custom Domain"
3. Add your domain (e.g., `api.yourdomain.com`)
4. Update DNS with provided CNAME

### Frontend Domain:

1. Go to frontend service settings
2. Click "Custom Domain"
3. Add your domain (e.g., `app.yourdomain.com`)
4. Update DNS with provided CNAME

5. Update `VITE_API_URL` and `CORS_ORIGINS` accordingly

## Step 5: Environment Variables Reference

### Required Variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection | Auto-provided by Render |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `PORT` | Application port | Auto-provided by Render |

### Optional Variables:

| Variable | Description |
|----------|-------------|
| `SENDGRID_API_KEY` | Email service |
| `SENDGRID_FROM_EMAIL` | Sender email |
| `TWILIO_ACCOUNT_SID` | SMS/WhatsApp |
| `TWILIO_AUTH_TOKEN` | Twilio auth |
| `TWILIO_WHATSAPP_NUMBER` | WhatsApp number |
| `TWILIO_SMS_NUMBER` | SMS number |
| `CALENDLY_API_KEY` | Calendar integration |
| `CALENDLY_EVENT_TYPE_UUID` | Event type |
| `HUBSPOT_API_KEY` | CRM integration |
| `HUBSPOT_PORTAL_ID` | HubSpot portal |
| `CLEARBIT_API_KEY` | Data enrichment |
| `HUNTER_API_KEY` | Email verification |

## Step 6: Monitoring & Logs

### View Logs:

1. **Backend Logs**:
   - Go to backend service
   - Click "Logs" tab
   - View real-time logs

2. **Frontend Logs**:
   - Go to frontend static site
   - Click "Logs" tab

### Monitor Performance:

- Render Dashboard shows:
  - CPU usage
  - Memory usage
  - Request metrics
  - Response times

### Set Up Alerts:

1. Go to service settings
2. Navigate to "Notifications"
3. Add email or Slack webhook

## Step 7: Continuous Deployment

Render automatically deploys on git push:

```bash
git add .
git commit -m "Update feature"
git push origin main
# Render auto-deploys
```

### Deployment Branches:

Configure different branches for environments:

- `main` → Production
- `staging` → Staging environment
- `dev` → Development

## Troubleshooting

### Deployment Failed

**Check build logs**:
- Look for dependency errors
- Verify Python/Node versions
- Check syntax errors

**Common issues**:
```bash
# Missing dependencies
pip install -r requirements.txt

# Wrong Python version
# Set PYTHON_VERSION=3.11.0 in environment

# Database connection
# Verify DATABASE_URL is set correctly
```

### Database Connection Error

1. Verify `DATABASE_URL` is set
2. Check database is running
3. Ensure database internal URL is used (not external)

### CORS Errors

Update `CORS_ORIGINS` in backend to include frontend URL:

```python
CORS_ORIGINS="https://your-frontend.onrender.com"
```

### OpenAI API Errors

1. Verify API key is correct
2. Check API usage limits
3. Ensure billing is set up

### Slow Performance (Free Tier)

Free tier services spin down after inactivity:

**Solutions**:
1. Upgrade to paid tier ($7/month)
2. Use external monitoring to ping periodically
3. Implement caching

## Cost Optimization

### Free Tier Limits:

- 750 hours/month for web services
- Free PostgreSQL (90-day retention)
- 100GB bandwidth/month

### Recommended Plan for Production:

**Starter Tier** (~$14/month):
- Backend: Starter ($7/month)
- Database: Starter ($7/month)
- Frontend: Free (static site)

**Professional Tier** (~$60/month):
- Backend: Standard ($25/month)
- Database: Standard ($20/month)
- Additional services as needed

## Scaling Considerations

### Horizontal Scaling:

Render supports:
- Multiple instances
- Load balancing
- Auto-scaling

### Database Scaling:

- Increase database plan for more connections
- Add read replicas
- Enable connection pooling

### CDN for Frontend:

1. Enable Render CDN
2. Or use Cloudflare for additional caching

## Security Best Practices

1. **Use Environment Variables**: Never commit secrets
2. **Enable HTTPS**: Automatic with Render
3. **Restrict CORS**: Whitelist specific domains
4. **Rotate API Keys**: Regularly update credentials
5. **Monitor Logs**: Watch for suspicious activity
6. **Database Backups**: Enable automatic backups

## Backup & Recovery

### Database Backups:

Render automatically backs up databases:
- Daily backups (retained 7 days on free tier)
- Configure retention period in settings

### Restore from Backup:

1. Go to database service
2. Click "Backups" tab
3. Select backup to restore
4. Create new database from backup

## Alternative Deployment Options

### Heroku:
Similar to Render, requires `Procfile` and `requirements.txt`

### AWS:
- Elastic Beanstalk for backend
- S3 + CloudFront for frontend
- RDS for PostgreSQL

### DigitalOcean:
- App Platform for deployment
- Managed databases available

### Railway:
- Similar to Render
- Simple deployment process

## Support Resources

- Render Documentation: https://render.com/docs
- Render Community: https://community.render.com
- Status Page: https://status.render.com

## Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Environment variables configured
- [ ] Database created and connected
- [ ] Backend deployed and healthy
- [ ] Frontend deployed and accessible
- [ ] Database initialized
- [ ] CORS configured correctly
- [ ] Test lead creation working
- [ ] OpenAI integration working
- [ ] Custom domain configured (if applicable)
- [ ] Monitoring and alerts set up
- [ ] Backup strategy in place
