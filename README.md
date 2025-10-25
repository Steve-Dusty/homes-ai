# Real Estate Agent - AI-Powered Property Search

An intelligent real estate search platform powered by Fetch.ai uAgents, ASI-1 mini, and MCP tools. Natural conversation meets property discovery.

## Features

- **Natural Conversation** - Talk to the AI agent like a real estate professional
- **Smart Recommendations** - Get location suggestions based on your job and lifestyle
- **Multi-Source Search** - Powered by Tavily and BrightData MCP integrations
- **Interactive Map** - Visualize properties on Mapbox with real-time data
- **No AI Slop** - Straightforward, helpful responses without robotic repetition

## Architecture

```
Frontend (Next.js)
  ↓ API Routes
Backend (uAgents)
  ↓
┌─────────────────┐
│ Scoping Agent   │ → Natural conversation (ASI-1 mini)
│ (Port 8001)     │ → Gathers: location, budget, beds, baths
└─────────────────┘
  ↓ criteria
┌─────────────────┐
│ Research Agent  │ → Searches properties via MCP
│ (Port 8002)     │ → Tavily: Web search
└─────────────────┘ → BrightData: Real estate scraping
  ↓ properties
┌─────────────────┐
│ Mapbox Agent    │ → Interactive map visualization
│ (Port 8003)     │ → Real coordinates from BrightData
└─────────────────┘
```

## Tech Stack

**Backend:**
- Fetch.ai uAgents (pure REST, no FastAPI)
- ASI-1 mini for natural language
- Tavily MCP for web search
- BrightData MCP for property data
- Mapbox for visualization

**Frontend:**
- Next.js 15
- React 19
- TypeScript
- Mapbox GL JS
- Tailwind CSS

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure .env
cp .env.example .env
# Add your API keys

# Start all agents
./start_all.sh

# Or start individually:
python agents/scoping_agent.py   # Port 8001
python agents/research_agent.py  # Port 8002
python agents/mapbox_agent.py    # Port 8003
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
echo "NEXT_PUBLIC_MAPBOX_API_KEY=your_mapbox_key" > .env.local

# Start dev server
npm run dev
```

### 3. Open Browser

Navigate to `http://localhost:3000`

## Environment Variables

### Backend (.env)

```bash
ASI_API_KEY=your_asi_api_key
TAVILY_API_KEY=your_tavily_key
BRIGHT_DATA_API_KEY=your_brightdata_key
MAPBOX_API_KEY=your_mapbox_key
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_MAPBOX_API_KEY=your_mapbox_key
SCOPING_AGENT_URL=http://localhost:8001
RESEARCH_AGENT_URL=http://localhost:8002
```

## Usage Example

**User:** Hi, I'm looking for a place in the Bay Area

**Agent:** Hey there! It's awesome that you're thinking about finding a home in the Bay Area. Do you have any specific area in mind? Like San Francisco, East Bay, or somewhere like Palo Alto?

**User:** I work in tech in Mountain View, budget is 1.5M, need 3 bedrooms and 2 bathrooms

**Agent:** Nice! With a tech job in Mountain View, you're right in the heart of Silicon Valley. A budget of $1.5M and 3 beds/2 baths sounds doable. Besides Mountain View, nearby areas like Sunnyvale, Santa Clara, or San Jose could be great options with good schools. Any other must-haves like a backyard?

**User:** Good schools are important, and a backyard would be nice. Ready to search

**Agent:** Perfect! I've found 10 properties matching your criteria...

*[Properties appear on the map]*

## Project Structure

```
estate/
├── backend/
│   ├── agents/
│   │   ├── scoping_agent.py      # Natural conversation
│   │   ├── research_agent.py     # Property search
│   │   └── mapbox_agent.py       # Visualization
│   ├── utils/
│   │   ├── asi_client.py         # ASI-1 mini wrapper
│   │   └── mcp_client.py         # MCP clients
│   ├── start_all.sh              # Start all agents
│   ├── stop_all.sh               # Stop all agents
│   └── README.md
│
└── frontend/
    ├── app/
    │   ├── api/chat/route.ts     # API integration
    │   └── page.tsx              # Main page
    ├── components/
    │   ├── ChatInterface.tsx     # Chat UI
    │   └── MapView.tsx           # Map UI
    └── lib/
        └── mockData.ts           # Fallback data
```

## API Endpoints

### Backend

**Scoping Agent:**
```bash
POST http://localhost:8001/chat
{
  "text": "Looking for a 3br in SF",
  "session_id": "user123"
}
```

**Research Agent:**
```bash
POST http://localhost:8002/search
{
  "location": "Mountain View",
  "max_budget": 1500000,
  "bedrooms": 3,
  "bathrooms": 2,
  "preferences": ["good schools"],
  "session_id": "user123"
}
```

**Mapbox Agent:**
```bash
POST http://localhost:8003/visualize
{
  "properties": [...],
  "center_location": "Mountain View",
  "session_id": "user123"
}
```

### Frontend

**Chat API:**
```bash
POST /api/chat
{
  "message": "Looking for a home",
  "sessionId": "session_123"
}
```

## Design Decisions

1. **Pure uAgents** - No adapters, no LangGraph wrapping. Direct REST endpoints.
2. **ASI-1 mini** - Fast, natural conversations without Claude dependency.
3. **MCP via HTTP** - Direct SSE endpoint integration with Tavily and BrightData.
4. **Coordinate Extraction** - BrightData returns lat/lng for accurate map placement.
5. **Natural Flow** - Avoids "doesn't meet criteria" loops with context-aware responses.

## Development

```bash
# Backend
cd backend
python -m pytest tests/        # Run tests
python agents/scoping_agent.py # Dev mode

# Frontend
cd frontend
npm run dev                    # Dev server
npm run build                  # Production build
npm run lint                   # Lint check
```

## Troubleshooting

**Agents won't start:**
- Check API keys in `.env`
- Ensure ports 8001-8003 are free
- Activate venv: `source .venv/bin/activate`

**Frontend can't connect:**
- Check backend agents are running
- Verify CORS is enabled (included in uAgents)
- Check browser console for errors

**No properties showing:**
- Check MCP API keys are valid
- View research agent logs: `tail -f logs/research.log`
- Fall back to mock data if MCP fails

## Future Enhancements

- [ ] User authentication and saved searches
- [ ] Email alerts for new listings
- [ ] Property comparison tool
- [ ] Mortgage calculator integration
- [ ] Price history and trends
- [ ] Neighborhood insights
- [ ] Virtual tour scheduling

## License

MIT

## Acknowledgments

- Fetch.ai for uAgents framework
- Tavily for search MCP
- BrightData for scraping MCP
- Mapbox for visualization
