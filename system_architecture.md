## System Architecture for Facebook Ad Spy Tool

**1. Backend (Scraping & API):**

*   **Technology:** Python with Playwright for web scraping.
*   **Functionality:**
    *   Receives a list of Facebook Page IDs.
    *   Navigates to the Facebook Ads Library for each Page ID.
    *   Implements infinite scrolling to load all ads.
    *   Extracts relevant ad data (Page name, Ad media URL, Primary ad text, Start date, Platforms, CTA).
    *   Stores scraped data in a database.
    *   Exposes a RESTful API for the frontend to retrieve and search ad data.

**2. Database:**

*   **Technology:** SQLite (for simplicity and cheap hosting) or PostgreSQL (for scalability).
*   **Schema:** To be defined in the next step.

**3. Frontend (User Interface):**

*   **Technology:** React.js (as requested).
*   **Functionality:**
    *   Allows users to paste or upload a list of Facebook Page IDs.
    *   Displays scraped ad data in a clean, searchable table/dashboard.
    *   Provides filtering and search capabilities (keyword, page name, ad type).
    *   Displays ad media (images/videos) thumbnails.
    *   Presents ad details (primary text, start date, platforms, CTA).

**4. Hosting:**

*   **Backend:** Potentially a serverless function (e.g., AWS Lambda, Google Cloud Functions) or a small VPS (e.g., DigitalOcean, Linode) for the Playwright scraping, as it requires a browser environment. A Flask API could run on the same VPS or a separate one.
*   **Frontend:** Vercel or Netlify for static site hosting (React app).
*   **Database:** Managed database service (e.g., AWS RDS, Google Cloud SQL) or self-hosted on the VPS.

**Workflow:**

1.  User uploads/pastes Page IDs to the frontend.
2.  Frontend sends Page IDs to the backend API.
3.  Backend initiates scraping process for each Page ID.
4.  Scraped data is stored in the database.
5.  Frontend continuously queries the backend API to display updated ad data.
6.  Users can interact with the frontend to search and filter ads.

