# Carver Financial Services Website Chatbot - Setup Guide

## Overview

This chatbot is designed specifically for Carver Financial Services to provide website visitors with instant answers about services, team information, and general company details. The chatbot scrapes and learns from:

- https://carverfinancialservices.com/
- https://www.raymondjames.com/

**Important Safety Features:**
- ✅ Only provides information from the two authorized websites
- ✅ Does NOT provide personalized financial advice
- ✅ Does NOT make investment recommendations
- ✅ Does NOT provide tax advice
- ✅ Redirects users to contact advisors for specific financial guidance

## System Architecture

```
┌─────────────────┐
│   Website       │
│   (Frontend)    │
│                 │
│  [Chat Widget]  │ ← Embedded JavaScript widget
└────────┬────────┘
         │
         │ HTTP/REST
         ▼
┌─────────────────┐
│  FastAPI        │
│  Backend        │
│                 │
│  [Chatbot API]  │ ← Safety guardrails & routing
└────────┬────────┘
         │
         ├──────────┐
         ▼          ▼
┌──────────────┐ ┌──────────────┐
│  Supabase    │ │   OpenAI     │
│  Vector DB   │ │   GPT-4o     │
└──────────────┘ └──────────────┘
```

## Prerequisites

1. **Python 3.10+** installed on your system
2. **Supabase Account** (free tier works):
   - Sign up at https://supabase.com
   - Create a new project
3. **OpenAI API Key**:
   - Sign up at https://platform.openai.com
   - Generate an API key
4. **Web Server** (for production deployment):
   - Any server capable of running Python (AWS, DigitalOcean, Heroku, etc.)

## Step 1: Environment Setup

### 1.1 Create `.env` file

Create a file named `.env` in the project root with the following content:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
```

**How to get these values:**

**OpenAI API Key:**
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key and paste it in `.env`

**Supabase Configuration:**
1. Go to your Supabase project dashboard
2. Click on "Settings" (gear icon) → "API"
3. Copy the "Project URL" → This is your `SUPABASE_URL`
4. Copy the "service_role" key (NOT the anon key) → This is your `SUPABASE_SERVICE_KEY`

### 1.2 Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Setup Supabase Vector Database

### 2.1 Enable Vector Extension

In your Supabase project:

1. Go to the SQL Editor
2. Run this SQL command:

```sql
-- Enable the pgvector extension
create extension if not exists vector;
```

### 2.2 Create Documents Table

Run this SQL in the Supabase SQL Editor:

```sql
-- Create documents table
create table documents (
  id bigserial primary key,
  content text,
  metadata jsonb,
  embedding vector(1536)
);

-- Create an index for faster similarity searches
create index on documents using ivfflat (embedding vector_cosine_ops)
with (lists = 100);
```

### 2.3 Create Similarity Search Function

Run this SQL to create the search function:

```sql
-- Create function for similarity search
create or replace function match_documents (
  query_embedding vector(1536),
  match_threshold float,
  match_count int
)
returns table (
  id bigint,
  content text,
  metadata jsonb,
  similarity float
)
language sql stable
as $$
  select
    documents.id,
    documents.content,
    documents.metadata,
    1 - (documents.embedding <=> query_embedding) as similarity
  from documents
  where 1 - (documents.embedding <=> query_embedding) > match_threshold
  order by documents.embedding <=> query_embedding
  limit match_count;
$$;
```

## Step 3: Scrape and Ingest Website Data

Run the scraper to populate your database with website content:

```bash
python scrape_websites.py
```

This will:
- Crawl both carverfinancialservices.com and raymondjames.com
- Extract text content from up to 30 pages per website
- Split content into chunks
- Generate embeddings
- Store everything in Supabase

**Expected output:**
```
==================================================
Scraping https://carverfinancialservices.com/
==================================================

Found 25 pages to scrape
✓ Scraped: https://carverfinancialservices.com/
✓ Scraped: https://carverfinancialservices.com/about
...

==================================================
Total documents scraped: 50
==================================================

Split into 234 chunks
Storing documents in Supabase vector store...
✓ Successfully scraped and stored all website content!
Total chunks stored: 234
```

**Note:** This process may take 5-15 minutes depending on website size and your internet connection.

## Step 4: Start the Chatbot API

### 4.1 Local Testing

Start the FastAPI server locally:

```bash
python chatbot_api.py
```

Or use uvicorn directly:

```bash
uvicorn chatbot_api:app --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### 4.2 Test the API

Open your browser and go to:
- `http://localhost:8000` - Health check
- `http://localhost:8000/docs` - Interactive API documentation

Test a chat request:

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What services does Carver Financial Services offer?",
    "chat_history": []
  }'
```

## Step 5: Embed the Chatbot on Your Website

### 5.1 Simple Embed Method

Copy the entire content of `embed_snippet.html` and paste it just before the closing `</body>` tag on your website.

### 5.2 Update API URL

In the embedded code, find this line:

```javascript
const API_URL = 'http://localhost:8000/chat';
```

Change it to your production API URL:

```javascript
const API_URL = 'https://your-domain.com/chat';
```

### 5.3 Example Integration

```html
<!DOCTYPE html>
<html>
<head>
    <title>Carver Financial Services</title>
</head>
<body>
    <!-- Your website content here -->
    <header>...</header>
    <main>...</main>
    <footer>...</footer>

    <!-- PASTE CHATBOT CODE HERE (from embed_snippet.html) -->
    <style>
        /* Chatbot styles */
        ...
    </style>
    <div id="carver-chatbot-container">
        ...
    </div>
    <script>
        ...
    </script>
    <!-- END CHATBOT CODE -->

</body>
</html>
```

## Step 6: Production Deployment

### Option A: Deploy on Heroku

1. Create a `Procfile`:
```
web: uvicorn chatbot_api:app --host 0.0.0.0 --port $PORT
```

2. Deploy:
```bash
heroku create carver-chatbot
heroku config:set OPENAI_API_KEY=your_key
heroku config:set SUPABASE_URL=your_url
heroku config:set SUPABASE_SERVICE_KEY=your_key
git push heroku main
```

### Option B: Deploy on DigitalOcean App Platform

1. Create a new app from GitHub repository
2. Set environment variables in the app settings
3. Deploy with auto-scaling enabled

### Option C: Deploy on AWS EC2

1. Launch an Ubuntu EC2 instance
2. Install Python and dependencies
3. Use systemd or supervisor to keep the API running
4. Set up nginx as a reverse proxy
5. Configure SSL with Let's Encrypt

Example systemd service (`/etc/systemd/system/carver-chatbot.service`):

```ini
[Unit]
Description=Carver Financial Services Chatbot API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/chatbot
Environment="PATH=/home/ubuntu/chatbot/venv/bin"
ExecStart=/home/ubuntu/chatbot/venv/bin/uvicorn chatbot_api:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### Option D: Deploy with Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "chatbot_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t carver-chatbot .
docker run -p 8000:8000 --env-file .env carver-chatbot
```

## Step 7: SSL/HTTPS Setup (Important!)

For production, you MUST use HTTPS. Modern browsers block HTTP requests from HTTPS websites.

### Using nginx as reverse proxy:

```nginx
server {
    listen 443 ssl;
    server_name api.carverfinancialservices.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Get free SSL certificate with Let's Encrypt:
```bash
sudo certbot --nginx -d api.carverfinancialservices.com
```

## Maintenance

### Update Website Content

To refresh the chatbot's knowledge when website content changes:

```bash
python scrape_websites.py
```

**Recommended frequency:** Weekly or whenever major website updates are made

### Monitor Usage

Check API logs to see:
- Most common questions
- Error rates
- Response times

### Update Safety Guardrails

Edit `chatbot_api.py` to adjust the system prompt or add more restricted keywords.

## Customization

### Change Chatbot Appearance

Edit the CSS in `embed_snippet.html`:

```css
/* Change primary color */
#carver-chatbot-button {
    background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
}

/* Change size */
#carver-chatbot-window {
    width: 400px;  /* Adjust width */
    height: 600px; /* Adjust height */
}
```

### Change Chatbot Behavior

Edit the system prompt in `chatbot_api.py`:

```python
SYSTEM_PROMPT = """You are a helpful assistant...
[Customize instructions here]
"""
```

### Add More Data Sources

To include additional websites, edit `scrape_websites.py`:

```python
websites = [
    "https://carverfinancialservices.com/",
    "https://www.raymondjames.com/",
    "https://your-additional-site.com/"  # Add here
]
```

## Troubleshooting

### Chatbot won't load
- Check that the API is running
- Verify the API_URL is correct
- Check browser console for CORS errors

### No responses or errors
- Verify OpenAI API key is valid and has credits
- Check Supabase connection
- Review API logs for errors

### Responses are incorrect
- Re-run the scraper to update knowledge
- Check that websites are accessible
- Verify vector database has content

### CORS errors
- Ensure FastAPI CORS middleware is configured
- Check that frontend domain is allowed

## Support

For issues or questions:
1. Check the logs: `tail -f /var/log/chatbot.log`
2. Test API directly: `http://your-api-url/docs`
3. Verify environment variables are set correctly

## Security Checklist

- [ ] `.env` file is NOT committed to git
- [ ] HTTPS is enabled in production
- [ ] CORS is restricted to your domain only
- [ ] API rate limiting is configured
- [ ] Supabase service key is kept secure
- [ ] OpenAI API usage is monitored

## Cost Estimates

**Typical monthly costs for moderate traffic (1000 conversations/month):**

- OpenAI API: $10-30
- Supabase: Free (up to 500MB)
- Hosting: $5-20 (depending on provider)

**Total: ~$15-50/month**

## License

Ensure compliance with:
- OpenAI usage policies
- Website scraping terms of service
- Financial services regulations (no personalized advice)

---

**Last Updated:** 2025
**Version:** 1.0.0
