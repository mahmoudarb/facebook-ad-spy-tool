## Data Structure for Ad Spy Tool

**Database Schema:**

**1. Pages Table:**

```sql
CREATE TABLE pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_id TEXT UNIQUE NOT NULL,
    page_name TEXT,
    last_scraped TIMESTAMP,
    status TEXT DEFAULT 'pending' -- pending, scraping, completed, error
);
```

**2. Ads Table:**

```sql
CREATE TABLE ads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_id TEXT NOT NULL,
    library_id TEXT UNIQUE NOT NULL,
    ad_text TEXT,
    media_url TEXT,
    media_type TEXT, -- image, video
    start_date DATE,
    platforms TEXT, -- JSON array or comma-separated string
    cta TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (page_id) REFERENCES pages (page_id)
);
```

**3. Scraping Jobs Table (Optional, for tracking):**

```sql
CREATE TABLE scraping_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_ids TEXT, -- JSON array of page IDs
    status TEXT DEFAULT 'pending', -- pending, running, completed, error
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);
```

**API Data Models:**

**1. Page Model:**

```json
{
  "page_id": "20531316728",
  "page_name": "Facebook",
  "last_scraped": "2025-08-01T18:00:00Z",
  "status": "completed",
  "ad_count": 1000
}
```

**2. Ad Model:**

```json
{
  "id": 1,
  "page_id": "20531316728",
  "library_id": "1087496732800826",
  "ad_text": "Now, you can find every video you've liked, shared, or saved, all in your Reels Library. So you'll never lose that video you loved.",
  "media_url": "https://example.com/ad_media.jpg",
  "media_type": "image",
  "start_date": "2025-07-29",
  "platforms": ["Facebook", "Instagram"],
  "cta": "Learn More",
  "scraped_at": "2025-08-01T18:00:00Z"
}
```

**3. Scraping Job Model:**

```json
{
  "id": 1,
  "page_ids": ["20531316728", "12345678901"],
  "status": "running",
  "started_at": "2025-08-01T18:00:00Z",
  "completed_at": null,
  "error_message": null
}
```

**Frontend Data Structures:**

**1. Ad List State:**

```javascript
const [ads, setAds] = useState([]);
const [filteredAds, setFilteredAds] = useState([]);
const [searchTerm, setSearchTerm] = useState('');
const [filters, setFilters] = useState({
  pageId: '',
  platform: '',
  dateRange: { start: '', end: '' }
});
```

**2. Page List State:**

```javascript
const [pages, setPages] = useState([]);
const [selectedPages, setSelectedPages] = useState([]);
```

