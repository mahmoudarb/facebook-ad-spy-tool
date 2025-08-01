# Facebook Ad Spy Tool

A comprehensive web-based tool for scraping and analyzing Facebook ads from multiple pages using the Facebook Ads Library. Built with React frontend and Flask backend with Playwright for web scraping.

## 🚀 Features

- **Bulk Page Scraping**: Input multiple Facebook Page IDs to scrape all their ads
- **Real-time Job Tracking**: Monitor scraping progress with live status updates
- **Advanced Search & Filtering**: Search ads by text, filter by page, platform, or date
- **Professional Dashboard**: Clean, responsive interface with tabbed navigation
- **Ad Media Display**: View ad images and videos with thumbnails
- **Export Capabilities**: Data stored in structured format for easy export
- **Rate Limiting**: Built-in delays to avoid Facebook blocking
- **Error Handling**: Robust error handling for invalid pages and network issues

## 📋 Table of Contents

- [Demo](#demo)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [Legal Disclaimer](#legal-disclaimer)

## 🎯 Demo

### Dashboard Overview
![Dashboard](screenshots/dashboard.png)

### Scraping Interface
![Scraping](screenshots/scraping.png)

### Ad Results
![Results](screenshots/results.png)

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  Flask Backend  │    │ Facebook Ads    │
│                 │    │                 │    │ Library         │
│ - Dashboard     │◄──►│ - REST API      │◄──►│                 │
│ - Search/Filter │    │ - Playwright    │    │ - Public Data   │
│ - Real-time UI  │    │ - SQLite/Postgres│    │ - No API Key    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Tech Stack

**Frontend:**
- React 18
- Tailwind CSS
- shadcn/ui components
- Lucide icons
- Vite build tool

**Backend:**
- Flask (Python web framework)
- Playwright (browser automation)
- SQLAlchemy (database ORM)
- BeautifulSoup (HTML parsing)
- SQLite/PostgreSQL (database)

**Scraping:**
- Playwright with Chromium
- Infinite scroll handling
- Rate limiting and error handling
- Media URL extraction

## ⚡ Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### 1-Minute Setup

```bash
# Clone the repository
git clone <repository-url>
cd facebook-ad-spy-tool

# Start backend
cd facebook_ad_spy_backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
python src/main.py

# In a new terminal, start frontend
cd facebook-ad-spy-frontend
npm install
npm run dev

# Open http://localhost:5173 in your browser
```

## 🔧 Installation

### Backend Setup

1. **Create virtual environment:**
```bash
cd facebook_ad_spy_backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
playwright install chromium
```

3. **Initialize database:**
```bash
python src/main.py
# Database will be created automatically on first run
```

### Frontend Setup

1. **Install dependencies:**
```bash
cd facebook-ad-spy-frontend
npm install
```

2. **Start development server:**
```bash
npm run dev
```

### Environment Variables

Create a `.env` file in the backend directory:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///src/database/app.db
SCRAPING_DELAY=2
MAX_ADS_PER_PAGE=100
```

## 📖 Usage

### 1. Starting a Scraping Job

1. Navigate to the "Scrape Ads" tab
2. Enter Facebook Page IDs (one per line):
   ```
   20531316728
   104958162837
   40796308305
   ```
3. Click "Start Scraping"
4. Monitor progress in real-time

### 2. Browsing Results

1. Go to the "Browse Ads" tab
2. Use the search box to find specific ads
3. Filter by page using the dropdown
4. View ad details including:
   - Ad text and media
   - Start date and platforms
   - Call-to-action buttons

### 3. Managing Pages and Jobs

- **Pages Tab**: View all scraped pages and their status
- **Jobs Tab**: Monitor scraping job history and status

### Finding Facebook Page IDs

To find a Facebook Page ID:

1. Go to the Facebook page
2. View page source or use browser developer tools
3. Look for `"pageID":"123456789"` in the HTML
4. Or use online tools like "Find My Facebook ID"

### Example Page IDs

- Facebook: `20531316728`
- Nike: `104958162837`
- Coca-Cola: `40796308305`
- McDonald's: `56381779049`

## 📚 API Documentation

### Base URL
```
http://localhost:5001/api
```

### Endpoints

#### Get Statistics
```http
GET /stats
```

Response:
```json
{
  "success": true,
  "stats": {
    "total_pages": 5,
    "total_ads": 150,
    "recent_jobs": [...]
  }
}
```

#### Start Scraping Job
```http
POST /scrape
Content-Type: application/json

{
  "page_ids": ["20531316728", "104958162837"],
  "max_ads_per_page": 100
}
```

#### Get Ads
```http
GET /ads?page=1&per_page=50&search=keyword&page_id=123456789
```

#### Get Pages
```http
GET /pages
```

#### Get Jobs
```http
GET /jobs
```

#### Get Job Status
```http
GET /jobs/{job_id}
```

### Response Format

All API responses follow this format:
```json
{
  "success": true,
  "data": {...},
  "error": null
}
```

## 🚀 Deployment

### Quick Deploy Options

#### 1. Railway (Recommended for beginners)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

#### 2. Docker
```bash
# Build and run
docker build -t facebook-ad-spy .
docker run -p 5001:5001 facebook-ad-spy
```

#### 3. VPS (DigitalOcean, Linode)
```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip nodejs npm nginx

# Deploy application
git clone <your-repo>
# Follow installation steps
# Configure nginx reverse proxy
```

### Production Configuration

1. **Environment Variables:**
```env
FLASK_ENV=production
SECRET_KEY=strong-random-secret-key
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

2. **Database Migration:**
```bash
# For PostgreSQL
pip install psycopg2-binary
# Update DATABASE_URL in environment
```

3. **Frontend Build:**
```bash
cd facebook-ad-spy-frontend
npm run build
cp -r dist/* ../facebook_ad_spy_backend/src/static/
```

See [Deployment Guide](deployment_guide.md) for detailed instructions.

## 🔍 Troubleshooting

### Common Issues

#### "No ads found" for valid pages
- The page might not have any active ads
- Try different page IDs
- Check if the page exists and is public

#### Scraping jobs stuck in "pending"
- Check Flask backend logs
- Ensure Playwright browsers are installed
- Verify internet connection

#### Frontend can't connect to backend
- Ensure backend is running on port 5001
- Check CORS configuration
- Verify API endpoints are accessible

#### Browser automation fails
- Install Playwright browsers: `playwright install chromium`
- Check system dependencies: `playwright install-deps`
- Ensure sufficient memory (2GB+ recommended)

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Tips

1. **Limit concurrent scraping**: Process one page at a time
2. **Increase delays**: Set `SCRAPING_DELAY=3` for slower scraping
3. **Use PostgreSQL**: For better performance with large datasets
4. **Enable caching**: Cache API responses for better frontend performance

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes and test thoroughly**
4. **Commit with clear messages:**
   ```bash
   git commit -m "Add amazing feature"
   ```
5. **Push to your fork:**
   ```bash
   git push origin feature/amazing-feature
   ```
6. **Create a Pull Request**

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint/Prettier for React code
- Add tests for new features
- Update documentation
- Ensure all tests pass

### Code Structure

```
facebook-ad-spy-tool/
├── facebook_ad_spy_backend/
│   ├── src/
│   │   ├── models/          # Database models
│   │   ├── routes/          # API endpoints
│   │   ├── scraper/         # Scraping logic
│   │   └── main.py          # Flask app
│   ├── requirements.txt
│   └── Dockerfile
├── facebook-ad-spy-frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── hooks/          # Custom hooks
│   │   └── App.jsx         # Main app
│   └── package.json
└── README.md
```

## ⚖️ Legal Disclaimer

This tool is designed for educational and research purposes. Users are responsible for:

1. **Compliance with Terms of Service**: Ensure your use complies with Facebook's Terms of Service and Ads Library terms
2. **Rate Limiting**: The tool includes built-in delays to be respectful of Facebook's servers
3. **Data Usage**: Only use scraped data in accordance with applicable laws and regulations
4. **Commercial Use**: Consider legal implications before using for commercial purposes

### Important Notes

- This tool only accesses publicly available data from Facebook's Ads Library
- No Facebook API keys or authentication required
- Respects robots.txt and implements reasonable rate limiting
- Users should review and comply with all applicable terms and laws

### Recommended Usage

- **Research and Analysis**: Market research, competitive analysis, academic studies
- **Transparency**: Understanding political advertising, public interest research
- **Personal Use**: Learning about advertising strategies and trends

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Facebook for providing the public Ads Library
- Playwright team for excellent browser automation
- React and Flask communities for great frameworks
- All contributors and users of this tool

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Email**: your-email@example.com

---

**Built with ❤️ for the open source community**

