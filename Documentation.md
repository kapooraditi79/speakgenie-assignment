# Project Documentation: Approach & Resources

## 📚 1. Learning Resources & Tech Stack

This project integrates multiple data engineering concepts and third-party APIs. Below are the key resources and libraries utilized to build the system.

### **APIs & Data Sources**

- **YouTube Data API v3:** Used for fetching video metadata and statistics.
  - _Documentation:_ [Google Developers - YouTube API](https://developers.google.com/youtube/v3/docs)
  - _Key Endpoints:_ `search.list` (Discovery), `videos.list` (Enrichment).
- **Discourse API:** Used to mine the n8n Community Forum.
  - _Documentation:_ [Discourse API Docs](https://docs.discourse.org/)
  - _Key Endpoint:_ `search.json` with query parameters `order:views`.
- **Google Trends (Pytrends):** Used to analyze relative search interest and rising topics.
  - _Library:_ [Pytrends (Unofficial API)](https://pypi.org/project/pytrends/)

### **Core Libraries**

- **Flask (`flask`):** Selected for building a lightweight, RESTful API server.
- **MySQL Connector (`mysql-connector-python`):** For robust SQL interactions and connection pooling.
- **Pandas (`pandas`):** Used for time-series analysis on Google Trends data (calculating moving averages).

---

## 🛠 2. Detailed Technical Approach

The system follows a classic **ETL (Extract, Transform, Load)** architecture designed for fault tolerance and scalability.

### **Phase 1: Extraction (Data Sourcing)**

We employ a multi-source strategy to ensure a holistic view of "popularity," capturing both historical utility (YouTube/Forum) and current hype (Trends).

1. **YouTube Fetcher (`fetch_youtube.py`):**
   - **Challenge:** The search endpoint does not return statistics (views/likes), only titles.
   - **Solution:** Implemented a **Two-Step Batch Fetch** .
     1. _Discovery:_ Search for keywords (e.g., "n8n workflow") to get Video IDs.
     2. _Enrichment:_ Send a batch request (up to 50 IDs at once) to the `videos` endpoint to retrieve statistics efficiently (saving 99% of API quota).
2. **Forum Fetcher (`fetch_forum.py`):**
   - **Strategy:** Uses the public Discourse search API sorted by `views`.
   - **Constraint Handling:** Implemented pagination limits (max 4 pages) to respect API depth limits and avoid 429/400 errors.
3. **Google Trends Fetcher (`fetch_google.py`):**
   - **Granularity Fix:** Dynamically handles Data Granularity. If the API returns daily data, we analyze a 30-day window. If weekly, we adjust the window size to ensure accurate trend calculation.
   - **Geography:** Segmented queries by `US` and `IN` (India) to capture regional adoption differences.

### **Phase 2: Transformation (Analytics & Logic)**

Raw numbers are often misleading. We apply an analytical layer to determine **"Trustworthiness"** and **"True Popularity."**

- **Engagement Ratios (Quality Filter):**
  - We calculate the **Like-to-View Ratio** (**L**ik**es**÷**Vi**e**w**s).
  - _Insight:_ A ratio **<**1% suggests clickbait or low quality. A ratio **>**4% indicates high utility.
- **Weighted Popularity Score:**
  - _Formula:_ **S**core**=**Vi**e**w**s**+**(**L**ik**es**×**10**)**+**(**C**o**mm**e**n**t**s**×**20**)**
  - _Logic:_ We weigh active engagement (Likes/Comments) significantly higher than passive consumption (Views). This bubbles up "helpful" workflows over just "old" ones.
- **Trend Detection (Growth Metrics):**
  - For Google Trends, absolute numbers are relative (0-100).
  - _Logic:_ We calculate the **% Growth** between the last 30 days and the previous 30 days to identify "Breakout" topics.

### **Phase 3: Storage (Idempotent Design)**

- **Schema:** The MySQL database uses a hybrid schema.
  - _Standard Columns:_ `views`, `likes` (for YouTube/Forum).
  - _Flexible Column:_ `meta_data` (JSON) to store platform-specific metrics like "Trend Direction" or "Growth %" without polluting the main schema.
- **Idempotency:** The loading script uses `INSERT ... ON DUPLICATE KEY UPDATE`.
  - _Benefit:_ The script can be run daily without creating duplicate entries. It automatically recognizes existing URLs and updates their statistics.

### **Phase 4: Serving (Polymorphic API)**

- **Endpoint:** `/api/workflows`
- **Behavior:** The API response structure changes dynamically based on the source platform.
  - _YouTube:_ Returns `evidence: { views, likes }`.
  - _Trends:_ Returns `evidence: { growth_percentage, trend_direction }`.
  - _Why:_ This provides the frontend with the most contextually relevant metrics for each platform type.

---

## 🤖 3. Automation Strategy

The system is built as a **CLI-first application** (`main.py`), making it deployment-ready for standard schedulers.

- **Environment Variables:** All secrets (API Keys, DB Credentials) are decoupled from the code using `.env`, allowing safe deployment across different environments (Dev vs. Prod).
- **Fault Tolerance:** Each fetcher is wrapped in independent `try-except` blocks. If one API fails (e.g., API quota exceeded), the pipeline continues to process the other sources, ensuring partial data freshness rather than total failure.
- **Scheduling:** Validated for deployment via **Linux Crontab** (for production servers) and **Windows Task Scheduler** (for local automation).
