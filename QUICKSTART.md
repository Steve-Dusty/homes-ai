# Estate Search - Quick Start Guide

## 🚀 Running the Full Stack

### 1. Backend Setup (Python + uAgents)

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys:
#   - ASI_API_KEY
#   - TAVILY_API_KEY

# Start the API server
python api_server.py
```

The backend will start on **http://localhost:8080**

### 2. Frontend Setup (Next.js)

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will start on **http://localhost:3000**

## 🎯 How It Works

### Architecture Flow

```
User Message (Frontend)
    ↓
Next.js API Route (/api/chat)
    ↓
FastAPI Streaming Endpoint (localhost:8080/api/chat)
    ↓
EstateCoordinator Agent
    ↓
┌─────────────────┬──────────────────┐
│                 │                  │
Scoping Agent  Research Agent
    ↓                 ↓
ASI:1 LLM      Tavily Search + ASI:1
    ↓                 ↓
Streaming Updates ← ← ← Back to Frontend
```

### Real-Time Streaming

The system uses **NDJSON streaming** (newline-delimited JSON) to provide real-time updates:

1. **Agent Updates**: See which agent is processing
   ```json
   {"agent": "Scoping Agent", "message": "Processing...", "type": "scoping"}
   ```

2. **Final Results**: Properties and search summary
   ```json
   {
     "type": "complete",
     "result": {
       "properties": [...],
       "search_summary": "...",
       "requirements": {...}
     }
   }
   ```

## 📝 Example Conversation

**User:** "I'm looking for a house in Oakland"

**Scoping Agent:** "Great! What's your budget range?"

**User:** "Around $800k, need 3 bedrooms"

**Scoping Agent:** "Perfect! How many bathrooms?"

**User:** "2 bathrooms, prefer good schools"

**Coordinator:** ✅ Scoping complete! Triggering search...

**Research Agent:** 🔍 Searching properties on Zillow, Redfin, Realtor.com...

**Result:** Found 5 properties! *[Properties displayed on map]*

## 🛠️ Troubleshooting

### Backend Issues

**Port conflicts:**
```bash
# The system uses random ports 9000-9500 for agents
# If you get port errors, just restart
```

**Missing API keys:**
```bash
# Make sure .env has both keys:
cat backend/.env
```

**Agent timeout:**
```bash
# Increase timeout in main.py:189
max_timeout = 180  # 3 minutes
```

### Frontend Issues

**Can't connect to backend:**
```bash
# Check BACKEND_URL in frontend/app/api/chat/route.ts
# Default: http://localhost:8080
```

**Streaming not working:**
- Check browser console for errors
- Ensure backend is running and accessible
- Try curl test: `curl -X POST http://localhost:8080/api/chat -H "Content-Type: application/json" -d '{"message":"test","session_id":"1"}'`

## 🧪 Testing Individual Components

### Test Backend Agents Only

```bash
cd backend
python main.py
```

This runs a standalone test without the API server.

### Test API Server

```bash
# Terminal 1: Start API server
cd backend
python api_server.py

# Terminal 2: Test with curl
curl -N -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Looking for 3BR in SF","session_id":"test1"}'
```

You should see streaming NDJSON responses.

### Test Frontend Only

```bash
cd frontend
npm run dev
```

Frontend will show connection errors until backend is running.

## 📊 Monitoring

Watch the logs:

**Backend:**
- Agent initialization messages
- Protocol message handling
- LLM API calls
- Tavily search queries

**Frontend:**
- API route logs in terminal
- Browser console for streaming updates
- Network tab to see NDJSON stream

## 🔥 Common Commands

```bash
# Backend
cd backend && python api_server.py

# Frontend
cd frontend && npm run dev

# Test backend only
cd backend && python main.py

# Install backend deps
cd backend && pip install -r requirements.txt

# Install frontend deps
cd frontend && npm install
```

## ⚡ Production Tips

1. **Use production ASGI server:**
   ```bash
   gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **Set CORS properly:**
   ```python
   # In api_server.py
   allow_origins=["https://yourdomain.com"]
   ```

3. **Add rate limiting** to prevent API abuse

4. **Deploy agents to Agentverse** for hosted operation

5. **Use Redis** for session management across multiple workers

## 🎉 You're Ready!

Open http://localhost:3000 and start searching for properties!

The agents will:
1. ✅ Have natural conversations to gather requirements
2. 🔍 Search real estate sites via Tavily
3. 📍 Display results on an interactive Mapbox map
4. 📊 Show neighborhood statistics

Enjoy your AI-powered real estate search! 🏠
