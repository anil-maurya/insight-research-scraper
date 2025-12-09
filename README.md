# 📘 User Insight Data Collection Pipeline

A lightweight, founder-friendly system for collecting, cleaning, and analyzing user comments from public platforms (Reddit, YouTube, App Store, Instagram, etc.).

Designed for:

- **Insight generation**
- **User psychology analysis**
- **Competitor gap identification**
- **Product development clarity**

Not designed for:

- Heavy data engineering
- Complex ML pipelines
- Data science workflows

This system is intentionally simple.

---

## 🏗️ **Repository Structure**

```
data-collection/
│
├── scrapers/
│   ├── reddit_scraper.py
│   ├── youtube_scraper.py
│   ├── instagram_scraper.py   (optional)
│   ├── playstore_scraper.py   (optional)
│   └── config.py
│
├── etl/
│   ├── clean_text.py
│   ├── process_batch.py
│   ├── utils.py
│   └── schema.json
│
├── pipelines/
│   ├── run_reddit.sh
│   ├── run_youtube.sh
│   └── run_all.sh
│
├── storage/
│   ├── mongo_connection.py
│   ├── insert_raw.py
│   ├── insert_processed.py
│   └── test_connection.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── samples/
│
├── insights/
│   ├── prompts/
│   ├── analysis_notes.md
│   └── final_insights.md
│
├── config/
│   ├── credentials.example.json
│   ├── mongo.example.json
│   └── settings.yaml
│
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🚀 **Purpose of This Pipeline**

This repo gives you:

- A **repeatable way** to collect real user data
- Clean + structured JSON for analysis
- A simple way to store data in **MongoDB**
- A blueprint for running **AI-powered insight extraction**

This is the foundation for:

- Understanding user psychology
- Mapping unmet needs
- Identifying competitor blind spots
- Defining differentiation
- Designing your product in the right direction

---

## 🔧 **Installation**

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/data-collection.git
cd data-collection
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install requirements

```bash
pip install -r requirements.txt
```

### 4. Create your environment config

Copy the template:

```bash
cp .env.example .env
```

Fill in:

- Reddit API keys
- YouTube API key
- MongoDB connection string

---

## 🧱 **How It Works (Simple Overview)**

### **1. Run a scraper**

Example:

```bash
bash pipelines/run_reddit.sh
```

This will:

- Fetch comments
- Save raw JSON in `data/raw/reddit/`
- Insert raw JSON into MongoDB

---

### **2. Run ETL processing**

```bash
python etl/process_batch.py
```

This will:

- Clean text
- Normalize structure
- Save processed JSON in `data/processed/`
- Insert processed data into MongoDB

---

### **3. Analyze inside ChatGPT/Claude**

Copy the contents of:

```
insights/prompts/*
```

Use prompts like:

- “Cluster these comments into 10 themes.”
- “Extract top emotional triggers.”
- “Identify unmet needs.”
- “Map competitor failures from these comments.”

Document findings in:

```
insights/analysis_notes.md
```

---

## 🗄️ **MongoDB Collections**

Two collections are used:

### **1. raw_comments**

- Stores exact raw scraped comments
- No cleaning
- Useful for reruns and audits

### **2. processed_comments**

- Cleaned text
- Normalized structure
- Useful for AI analysis and search

---

## 📥 **Adding New Platforms**

Add a new scraper file in `/scrapers/`.
Output raw JSON to `/data/raw/<platform>/`.

Update pipeline scripts in `/pipelines/` if needed.

---

## 🚫 **Avoid Analysis Paralysis**

Follow these rules:

### **Rule 1: Limit scraping**

- 200–500 comments per platform
- No infinite pagination
- Quality > quantity

### **Rule 2: Limit cleaning**

Do basic cleaning only:

- lowercase
- remove emojis
- strip whitespace

### **Rule 3: Limit analysis passes**

- 1st pass = themes
- 2nd pass = persona notes
- STOP after pass 2

### **Rule 4: Set a deadline**

Complete the entire data collection stage in **7–10 days**.

---

## 🧪 **Testing Your Setup**

Test MongoDB connection:

```bash
python storage/test_connection.py
```

Test Reddit scraper (first run):

```bash
python scrapers/reddit_scraper.py
```

Check data folder:

```
data/raw/reddit/*.json
```

---

## 🧠 **Insight Workflow Summary**

```
Scrape → Clean → Store → AI Analyze → Insight Report
```

Outputs:

- User pains
- Desires
- Emotional triggers
- Competitor gaps
- Positioning opportunities
- Product direction clarity

This is your **Market Insight Engine**.

---

## 🪄 **Future Enhancements (Optional)**

These are optional — only if needed later:

- Add Elasticsearch for faster search
- Add vector DB for semantic search
- Automate pipelines via cron
- Dashboard with Metabase

But for now:
**Keep it simple. Keep moving. No overbuilding.**
