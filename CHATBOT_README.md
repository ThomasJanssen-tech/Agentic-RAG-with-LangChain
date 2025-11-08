# 🤖 Carver Financial Services Website Chatbot

A fully functional, embeddable AI chatbot designed specifically for the Carver Financial Services website. This chatbot provides instant answers about services, team information, and company details by intelligently searching content from authorized websites.

## ✨ Features

### 🎯 Smart & Safe
- ✅ **Website-Specific Knowledge**: Only answers questions using content from carverfinancialservices.com and raymondjames.com
- ✅ **No Financial Advice**: Built-in safety guardrails prevent unauthorized financial recommendations
- ✅ **Intelligent Routing**: Automatically directs complex inquiries to licensed advisors
- ✅ **Source Attribution**: Cites sources when providing information

### 🎨 User-Friendly Design
- ✅ **Professional UI**: Modern, responsive chatbot widget
- ✅ **Mobile-Friendly**: Works perfectly on phones, tablets, and desktops
- ✅ **Easy to Embed**: Simple copy-paste integration
- ✅ **Customizable**: Easy to match your brand colors and style

### ⚡ Powerful Technology
- ✅ **AI-Powered**: Uses OpenAI GPT-4o for natural conversations
- ✅ **Vector Search**: Fast, accurate information retrieval with Supabase
- ✅ **RESTful API**: Clean, well-documented API
- ✅ **Scalable**: Built with FastAPI for high performance

## 🚀 Quick Start

**Get up and running in 10 minutes!**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Setup database (run SQL in Supabase)
# See QUICKSTART.md for SQL commands

# 4. Scrape website content
python scrape_websites.py

# 5. Start the API
python chatbot_api.py

# 6. Embed on your website
# Copy code from embed_snippet.html
```

📖 **Full instructions**: See [QUICKSTART.md](QUICKSTART.md)

## 📋 Project Structure

```
Agentic-RAG-with-LangChain/
├── chatbot_api.py              # FastAPI backend with safety guardrails
├── scrape_websites.py          # Website scraper for content ingestion
├── chatbot_widget.html         # Full HTML demo of chatbot widget
├── embed_snippet.html          # Minified code for website embedding
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── CHATBOT_SETUP.md           # Complete setup & deployment guide
├── QUICKSTART.md              # 10-minute quick start guide
└── CHATBOT_README.md          # This file
```

## 🔒 Safety & Compliance

### Built-in Safety Features

1. **System Prompt Guardrails**
   - Explicitly instructs AI not to provide financial advice
   - Only uses information from authorized websites
   - Redirects sensitive questions to human advisors

2. **Keyword Detection**
   - Monitors for financial advice requests
   - Flags potentially sensitive queries
   - Adds extra context to prevent inappropriate responses

3. **Source Verification**
   - All information is traceable to source URLs
   - Only uses pre-scraped, approved content
   - Cannot access external information

### Compliance Notes

- ✅ Does NOT provide personalized financial advice
- ✅ Does NOT make investment recommendations
- ✅ Does NOT provide tax or legal advice
- ✅ Clearly disclaims that it's informational only
- ✅ Directs users to contact licensed advisors for specific needs

## 💻 API Documentation

### Endpoints

#### `POST /chat`
Send a message and receive a response.

**Request:**
```json
{
  "message": "What services does Carver Financial Services offer?",
  "chat_history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"}
  ]
}
```

**Response:**
```json
{
  "response": "Carver Financial Services offers comprehensive wealth management...",
  "sources": [
    "https://carverfinancialservices.com/services",
    "https://carverfinancialservices.com/about"
  ]
}
```

#### `GET /health`
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy"
}
```

### Interactive Docs

When running locally, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎨 Customization Guide

### Change Colors

Edit the CSS in `embed_snippet.html`:

```css
/* Primary brand color */
#carver-chatbot-button {
    background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
}

/* Message bubbles */
.carver-message.user .carver-message-content {
    background: #YOUR_COLOR;
}
```

### Change Size & Position

```css
/* Widget size */
#carver-chatbot-window {
    width: 400px;
    height: 600px;
}

/* Position on page */
#carver-chatbot-container {
    bottom: 20px;   /* Distance from bottom */
    right: 20px;    /* Distance from right */
    /* For left side, use: left: 20px; */
}
```

### Change Behavior

Edit `chatbot_api.py`:

```python
SYSTEM_PROMPT = """You are a helpful assistant for Carver Financial Services.
[Customize instructions here]
"""
```

### Add More Websites

Edit `scrape_websites.py`:

```python
websites = [
    "https://carverfinancialservices.com/",
    "https://www.raymondjames.com/",
    "https://your-additional-site.com/"  # Add more here
]
```

## 🌐 Deployment Options

### Recommended Platforms

| Platform | Difficulty | Cost | Best For |
|----------|-----------|------|----------|
| **Heroku** | Easy | $7/mo | Quick deployment |
| **DigitalOcean** | Medium | $5-20/mo | Flexibility |
| **AWS EC2** | Hard | $5-30/mo | Full control |
| **Railway** | Easy | $5/mo | Modern DevOps |
| **Render** | Easy | Free-$7/mo | Free tier available |

### Deployment Checklist

- [ ] Environment variables configured
- [ ] Database setup complete
- [ ] Website content scraped
- [ ] HTTPS/SSL enabled
- [ ] CORS configured for your domain
- [ ] API URL updated in embed code
- [ ] Monitoring/logging enabled
- [ ] Backup strategy in place

📖 **Full deployment guide**: See [CHATBOT_SETUP.md](CHATBOT_SETUP.md#step-6-production-deployment)

## 🔄 Maintenance

### Regular Updates

**Weekly**: Re-scrape websites to keep content fresh
```bash
python scrape_websites.py
```

**Monthly**:
- Review conversation logs
- Update safety guardrails if needed
- Check API costs and usage
- Update dependencies

### Monitoring

Track these metrics:
- API response times
- Error rates
- Most common questions
- OpenAI API costs
- Supabase storage usage

## 💰 Cost Breakdown

**Monthly costs for typical usage (1000 conversations):**

| Service | Cost | Notes |
|---------|------|-------|
| OpenAI API | $10-30 | GPT-4o + embeddings |
| Supabase | Free | Up to 500MB database |
| Hosting | $5-20 | Varies by provider |
| **Total** | **$15-50** | Scales with usage |

### Cost Optimization Tips

1. Use GPT-3.5-turbo instead of GPT-4o (10x cheaper)
2. Implement response caching
3. Add rate limiting
4. Monitor and set usage alerts

## 🛠 Technical Stack

- **Backend**: FastAPI (Python)
- **AI Model**: OpenAI GPT-4o
- **Vector Database**: Supabase (PostgreSQL + pgvector)
- **Embeddings**: OpenAI text-embedding-3-small
- **Frontend**: Vanilla JavaScript (no frameworks)
- **Styling**: CSS3 with modern features

## 📊 Performance

- **Response Time**: 1-3 seconds average
- **Accuracy**: Based on website content only
- **Availability**: 99.9% uptime (with proper hosting)
- **Concurrent Users**: Scales with hosting tier

## 🔍 SEO & Accessibility

- ✅ Does not interfere with page SEO
- ✅ ARIA labels for screen readers
- ✅ Keyboard navigation support
- ✅ Mobile-responsive design
- ✅ Lightweight (< 50KB total)

## 🐛 Troubleshooting

### Common Issues

**Chatbot doesn't appear**
- Check API is running
- Verify API_URL in embed code
- Check browser console for errors

**No responses**
- Verify OpenAI API key has credits
- Check Supabase connection
- Review API logs

**Incorrect answers**
- Re-run scraper to update content
- Verify websites are accessible
- Check database has content

**CORS errors**
- Update CORS settings in chatbot_api.py
- Ensure domain is whitelisted

📖 **More troubleshooting**: See [CHATBOT_SETUP.md](CHATBOT_SETUP.md#troubleshooting)

## 📝 Example Questions

The chatbot can answer questions like:

- "What services does Carver Financial Services offer?"
- "Who are the advisors at Carver Financial Services?"
- "How do I contact Carver Financial Services?"
- "What is Raymond James?"
- "Where is Carver Financial Services located?"
- "What are your office hours?"

## 🚫 What It Won't Answer

The chatbot will politely decline:

- Personalized investment advice
- Stock picks or recommendations
- Tax planning advice
- Account-specific questions
- Market predictions
- Anything not on the authorized websites

## 📄 License

See [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This chatbot provides general information only and does not constitute financial, investment, tax, or legal advice. Users should consult with licensed professionals for specific guidance.

## 🤝 Support

For issues:
1. Check documentation: [CHATBOT_SETUP.md](CHATBOT_SETUP.md)
2. Review API docs: http://localhost:8000/docs
3. Check logs for errors

---

**Version**: 1.0.0
**Last Updated**: 2025
**Built for**: Carver Financial Services

Made with ❤️ using LangChain, OpenAI, and Supabase
