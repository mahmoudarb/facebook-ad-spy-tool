# Facebook Ad Spy Tool - Deployment Guide

## Overview

This guide provides multiple deployment options for the Facebook Ad Spy Tool, ranging from simple hosting solutions to scalable cloud deployments.

## Architecture Summary

- **Backend**: Flask + Playwright + SQLite/PostgreSQL
- **Frontend**: React (built to static files)
- **Scraping**: Playwright with Chromium browser
- **Database**: SQLite (development) / PostgreSQL (production)

## Deployment Options

### 1. Simple VPS Deployment (Recommended for MVP)

**Platforms**: DigitalOcean, Linode, Vultr
**Cost**: $5-20/month
**Complexity**: Low

#### Setup Steps:

1. **Server Requirements**:
   - Ubuntu 20.04+ or similar
   - 2GB RAM minimum (4GB recommended)
   - 20GB storage
   - Node.js 18+, Python 3.11+

2. **Installation Script**:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip nodejs npm git nginx

# Install PM2 for process management
sudo npm install -g pm2

# Clone your repository
git clone <your-repo-url>
cd facebook-ad-spy-tool

# Setup backend
cd facebook_ad_spy_backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Setup frontend
cd ../facebook-ad-spy-frontend
npm install
npm run build

# Copy built frontend to Flask static directory
cp -r dist/* ../facebook_ad_spy_backend/src/static/
```

3. **Process Management**:
```bash
# Start backend with PM2
cd facebook_ad_spy_backend
pm2 start "python src/main.py" --name "ad-spy-backend"
pm2 startup
pm2 save
```

4. **Nginx Configuration**:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Pros**: Simple, cost-effective, full control
**Cons**: Manual scaling, server maintenance required

---

### 2. Railway Deployment (Easiest)

**Platform**: Railway.app
**Cost**: $5-20/month
**Complexity**: Very Low

#### Setup Steps:

1. **Prepare for Railway**:
```bash
# Create railway.json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd facebook_ad_spy_backend && python src/main.py",
    "healthcheckPath": "/api/stats"
  }
}

# Create Procfile
web: cd facebook_ad_spy_backend && python src/main.py
```

2. **Deploy**:
   - Connect GitHub repository to Railway
   - Set environment variables
   - Deploy automatically

**Pros**: Zero configuration, automatic scaling, built-in database
**Cons**: Limited customization, vendor lock-in

---

### 3. Heroku Deployment

**Platform**: Heroku
**Cost**: $7-25/month
**Complexity**: Low

#### Setup Steps:

1. **Create Heroku Files**:
```bash
# Procfile
web: cd facebook_ad_spy_backend && gunicorn src.main:app

# runtime.txt
python-3.11.0

# requirements.txt (add to backend)
gunicorn==21.2.0
```

2. **Buildpacks**:
```bash
heroku buildpacks:add heroku/python
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-playwright
```

3. **Deploy**:
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

**Pros**: Easy deployment, add-ons ecosystem
**Cons**: Expensive for scaling, limited free tier

---

### 4. Docker + Cloud Run (Google Cloud)

**Platform**: Google Cloud Run
**Cost**: Pay-per-use, ~$10-50/month
**Complexity**: Medium

#### Setup Steps:

1. **Create Dockerfile**:
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright
RUN pip install playwright
RUN playwright install chromium

# Copy application
COPY facebook_ad_spy_backend /app/backend
COPY facebook-ad-spy-frontend/dist /app/backend/src/static

WORKDIR /app/backend

# Install Python dependencies
RUN pip install -r requirements.txt

EXPOSE 8080
CMD ["python", "src/main.py"]
```

2. **Deploy to Cloud Run**:
```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT-ID/ad-spy-tool

# Deploy
gcloud run deploy ad-spy-tool \
  --image gcr.io/PROJECT-ID/ad-spy-tool \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Pros**: Serverless scaling, pay-per-use, managed infrastructure
**Cons**: Cold starts, complexity

---

### 5. AWS EC2 + RDS (Enterprise)

**Platform**: Amazon Web Services
**Cost**: $50-200+/month
**Complexity**: High

#### Components:
- **EC2**: Application server
- **RDS**: PostgreSQL database
- **CloudFront**: CDN for frontend
- **Load Balancer**: High availability
- **Auto Scaling**: Handle traffic spikes

#### Setup Steps:
1. Launch EC2 instance (t3.medium or larger)
2. Set up RDS PostgreSQL instance
3. Configure security groups
4. Deploy application using similar VPS steps
5. Set up CloudFront distribution
6. Configure auto-scaling group

**Pros**: Enterprise-grade, highly scalable, many services
**Cons**: Complex setup, expensive, requires AWS expertise

---

## Database Considerations

### Development: SQLite
- Included in the current setup
- Zero configuration
- Perfect for testing and small deployments

### Production: PostgreSQL
- Recommended for production use
- Better concurrent access
- More robust for scaling

#### Migration to PostgreSQL:
```python
# Update requirements.txt
psycopg2-binary==2.9.7

# Update Flask config
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@host:5432/dbname'
```

## Environment Variables

Set these environment variables for production:

```bash
# Flask
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# Database (if using PostgreSQL)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Optional: Rate limiting
SCRAPING_DELAY=3
MAX_ADS_PER_PAGE=100
```

## Performance Optimization

### 1. Frontend Optimization
```bash
# Build optimized frontend
npm run build

# Serve static files with nginx (VPS deployment)
location /static/ {
    alias /path/to/static/files/;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 2. Backend Optimization
```python
# Add caching
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@cache.cached(timeout=300)
def get_stats():
    # Cached for 5 minutes
    pass
```

### 3. Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX idx_ads_page_id ON ads(page_id);
CREATE INDEX idx_ads_scraped_at ON ads(scraped_at);
CREATE INDEX idx_pages_status ON pages(status);
```

## Security Considerations

1. **Rate Limiting**: Implement rate limiting to prevent abuse
2. **Input Validation**: Validate page IDs before processing
3. **HTTPS**: Always use HTTPS in production
4. **Environment Variables**: Never commit secrets to version control
5. **CORS**: Configure CORS properly for production domains

## Monitoring and Logging

### Basic Monitoring
```python
import logging
logging.basicConfig(level=logging.INFO)

# Add request logging
@app.after_request
def log_request(response):
    app.logger.info(f'{request.method} {request.path} - {response.status_code}')
    return response
```

### Advanced Monitoring (Production)
- **Sentry**: Error tracking
- **New Relic**: Performance monitoring
- **DataDog**: Infrastructure monitoring

## Cost Estimates

| Platform | Setup | Monthly Cost | Scaling |
|----------|-------|--------------|---------|
| VPS (DigitalOcean) | Manual | $10-40 | Manual |
| Railway | Automatic | $5-20 | Automatic |
| Heroku | Easy | $25-100 | Automatic |
| Google Cloud Run | Medium | $10-50 | Automatic |
| AWS (Full Stack) | Complex | $50-200+ | Automatic |

## Recommended Deployment Path

### Phase 1: MVP (Railway/VPS)
- Start with Railway for quick deployment
- Or use a $10 VPS for more control
- Use SQLite database
- Single server setup

### Phase 2: Growth (Cloud Run/Heroku)
- Migrate to Cloud Run or Heroku
- Switch to PostgreSQL
- Add monitoring and logging
- Implement caching

### Phase 3: Scale (AWS/GCP Full Stack)
- Multi-region deployment
- Load balancing
- Auto-scaling
- CDN for static assets
- Managed database with replicas

## Support and Maintenance

1. **Regular Updates**: Keep dependencies updated
2. **Backup Strategy**: Regular database backups
3. **Monitoring**: Set up alerts for errors and performance
4. **Documentation**: Maintain deployment documentation
5. **Testing**: Implement CI/CD for automated testing

Choose the deployment option that best fits your budget, technical expertise, and scaling requirements. Start simple and scale up as needed.

