# Quick Start Guide - Carver Financial Services Chatbot

## 🚀 Get Running in 10 Minutes

### Prerequisites
- Python 3.10+
- Supabase account (free)
- OpenAI API key

### Step 1: Clone and Install (2 minutes)

```bash
# Navigate to project directory
cd Agentic-RAG-with-LangChain

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment (3 minutes)

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGxxxxxxxxxxxxxxx
```

**Get these values:**
- OpenAI: https://platform.openai.com/api-keys
- Supabase URL & Key: Your Supabase project → Settings → API

### Step 3: Setup Database (2 minutes)

In Supabase SQL Editor, run:

```sql
-- Enable vector extension
create extension if not exists vector;

-- Create documents table
create table documents (
  id bigserial primary key,
  content text,
  metadata jsonb,
  embedding vector(1536)
);

-- Create index
create index on documents using ivfflat (embedding vector_cosine_ops)
with (lists = 100);

-- Create search function
create or replace function match_documents (
  query_embedding vector(1536),
  match_threshold float default 0.5,
  match_count int default 5
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

### Step 4: Scrape Websites (5-10 minutes)

```bash
python scrape_websites.py
```

Wait for it to complete. You should see:
```
✓ Successfully scraped and stored all website content!
Total chunks stored: 234
```

### Step 5: Start the API (30 seconds)

```bash
python chatbot_api.py
```

### Step 6: Test It Works

Open browser to: http://localhost:8000/docs

Try the `/chat` endpoint with:
```json
{
  "message": "What services does Carver Financial Services offer?",
  "chat_history": []
}
```

### Step 7: Add to Website

1. Open `embed_snippet.html`
2. Copy all the code
3. Paste before `</body>` tag on your website
4. Change API_URL to your production URL

```javascript
// In the embedded code, change:
const API_URL = 'http://localhost:8000/chat';

// To your production URL:
const API_URL = 'https://your-api-domain.com/chat';
```

## ✅ That's It!

Your chatbot is now ready to use!

## 🔄 Updating Content

When website content changes, re-run:

```bash
python scrape_websites.py
```

## 🚨 Common Issues

**"No module named X"**
```bash
pip install -r requirements.txt
```

**"Connection refused"**
- Check your .env file has correct credentials
- Verify Supabase project is active

**"OpenAI rate limit"**
- Check you have API credits: https://platform.openai.com/usage
- Add payment method if needed

**Chatbot won't appear on website**
- Check browser console for errors
- Verify API_URL is correct
- Make sure API is running

## 📚 Full Documentation

See [CHATBOT_SETUP.md](CHATBOT_SETUP.md) for complete deployment guide.

## 🎨 Customization

**Change colors** - Edit CSS in `embed_snippet.html`:
```css
#carver-chatbot-button {
    background: linear-gradient(135deg, #YOUR_COLOR 0%, #YOUR_COLOR 100%);
}
```

**Change behavior** - Edit system prompt in `chatbot_api.py`

**Change position** - In CSS, change:
```css
#carver-chatbot-container {
    bottom: 20px;  /* Distance from bottom */
    right: 20px;   /* Distance from right */
}
```

## 💡 Tips

1. **Test locally first** - Always test with `http://localhost:8000` before deploying
2. **Use HTTPS in production** - Required for modern browsers
3. **Monitor costs** - Check OpenAI usage regularly
4. **Update weekly** - Re-scrape websites to keep content fresh
5. **Check logs** - Monitor for errors and common questions

## 🔐 Security Reminders

- ✅ Never commit `.env` file to git
- ✅ Use HTTPS in production
- ✅ Restrict CORS to your domain
- ✅ Monitor API usage for abuse
- ✅ The chatbot does NOT provide financial advice

## 📞 Need Help?

1. Check the full setup guide: `CHATBOT_SETUP.md`
2. Review API docs: `http://localhost:8000/docs`
3. Check logs for error messages

---

**Ready to deploy?** See production deployment options in [CHATBOT_SETUP.md](CHATBOT_SETUP.md#step-6-production-deployment)
