# n8n Workflow Popularity Engine

A production-ready data pipeline that identifies popular n8n workflows across YouTube, the n8n Community Forum, and Google Trends. It aggregates data, calculates "Trust Scores" based on community engagement, and serves the results via a REST API.

## 📦 Deliverables

1. **Automated ETL Pipeline (`main.py`):** Fetches and updates data idempotently (no duplicates).
2. **REST API (`api.py`):** Serves the curated dataset as JSON.
3. **Dataset Dump (`workflows_dump.sql`):** Pre-fetched dataset containing **over 50 workflows** with popularity evidence, ready for import.

## 🚀 Setup & Installation

### 1. Environment Setup

Clone the repository and install dependencies.

```bash
# Install required libraries
pip install -r requirements.txt
```

### 2. Database Configuration

You have two options to run this project:

#### **Option A: Quick Start (No API Keys Required)**

Use the provided SQL dump to verify the API and Data Richness immediately.

1. Create a MySQL database named `n8n_workflows`.
2. Import the pre-fetched data:
   **Bash**

   ```
   mysql -u root -p n8n_workflows < workflows_dump.sql
   ```

3. Create a `.env` file (copy from `.env.example`) and fill in your DB credentials:
   **Ini, TOML**

   ```
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=yourpassword
   DB_NAME=n8n_workflows
   ```

4. Start the API:
   **Bash**

   ```
   python src/api.py
   ```

#### **Option B: Run the Full Fetcher (Requires API Key)**

If you want to run the scraper engine yourself:

1. Add your `YOUTUBE_API_KEY` to the `.env` file.
2. Run the engine:
   **Bash**

   ```
   python src/main.py
   ```

## 📡 API Usage

Once `src/api.py` is running (default port 5000), you can access the following endpoints:

| **Goal**           | **URL**                                                        | **Description**                             |
| ------------------ | -------------------------------------------------------------- | ------------------------------------------- |
| **See Everything** | `http://127.0.0.1:5000/api/workflows`                          | Returns all workflows sorted by popularity. |
| **YouTube Only**   | `http://127.0.0.1:5000/api/workflows?platform=YouTube`         | Returns videos with View/Like stats.        |
| **Forum Only**     | `http://127.0.0.1:5000/api/workflows?platform=n8n%20Forum`     | Returns discussions with Reply counts.      |
| **Trending Now**   | `http://127.0.0.1:5000/api/workflows?platform=Google%20Trends` | Returns rising topics with Growth %.        |

## 🤖 Automation (Cron Job)

This system is designed to run automatically on a schedule.

Deployment Strategy:

#### Option 1: To deploy this on a Linux server (e.g., AWS EC2, DigitalOcean), use crontab.

1. Open the cron editor:
   **Bash**

   ```
   crontab -e
   ```

2. Add the daily schedule (Midnight run):
   **Bash**

   ```
   0 0 * * * cd /home/user/n8n-project/src && /usr/bin/python3 main.py >> /var/log/n8n_cron.log 2>&1
   ```

#### Option 2: Windows (Local Development)

To automate this on a Windows machine, use **Task Scheduler** :

1. Open **Task Scheduler** and click **"Create Basic Task..."**
2. **Name:** `n8n Popularity Fetcher` -> **Trigger:** `Daily`.
3. **Action:** `Start a program`.
4. **Settings:**
   - **Program/script:** `python` (or full path to python.exe).
   - **Add arguments:** `main.py`
   - **Start in:** `C:\Path\To\Your\Project\src` (CRITICAL: Must point to the folder containing .env).
5. Click **Finish** .

## 🧠 Approach & Analytics

- **Data Trustworthiness:** We calculate a "Like-to-View Ratio" to filter out low-quality content.
- **Popularity Score:** `Views + (Likes * 10) + (Comments * 20)`. This weighted score prioritizes high-engagement content (comments/likes) over passive views.
- **Trend Detection:** Uses Google Trends relative volume to detect breakout topics (+% Growth) that haven't hit YouTube yet.

## 📂 Project Structure

- `src/main.py`: The ETL Engine (Entry point).
- `src/api.py`: The Flask API Server.
- `src/fetch_*.py`: Modular scrapers for each platform.
- `src/database.py`: Database connection logic.
- `src/workflows_dump.sql`: Data backup.

## 📝 Sample API Responses

The API returns a **polymorphic `evidence` object** that changes structure based on the data source.

### 1. YouTube (Standard Metrics)

_Focuses on View Counts and Engagement Ratios._

```json
{
  "workflow": "Automate Gmail with n8n",
  "platform": "YouTube",
  "country": "US",
  "link": "[https://www.youtube.com/watch?v=12345](https://www.youtube.com/watch?v=12345)",
  "evidence": {
    "views": 15200,
    "likes": 450,
    "comments": 32,
    "engagement_score": 19700.0
  }
}
```

### 2. Google Trends (Growth Metrics)

_Focuses on Rising Trends and Percentage Growth (No absolute view counts)._

**JSON**

```json
{
  "workflow": "n8n deepseek integration",
  "platform": "Google Trends",
  "country": "US",
  "link": "[https://trends.google.com/trends/explore?q=n8n%20deepseek](https://trends.google.com/trends/explore?q=n8n%20deepseek)",
  "evidence": {
    "popularity_index": 142.0,
    "growth_percentage": 200,
    "trend_direction": "UP",
    "insight": "Trending UP 200.0% in last 30 days"
  }
}
```

### 3. n8n Forum (Community Metrics)

_Focuses on Discussion Depth (Replies)._

**JSON**

```json
{
  "workflow": "Whatsapp Integration Error 400",
  "platform": "n8n Forum",
  "country": "Global",
  "link": "[https://community.n8n.io/t/whatsapp-error/9988](https://community.n8n.io/t/whatsapp-error/9988)",
  "evidence": {
    "views": 2500,
    "likes": 15,
    "comments": 8, // Represents number of replies
    "engagement_score": 2810.0
  }
}
```

Thank you.
