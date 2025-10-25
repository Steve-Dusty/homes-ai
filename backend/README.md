# Estate Search uAgents Backend

A multi-agent system built with **Fetch.ai uAgents** for Bay Area real estate search powered by ASI:1 LLM and Tavily search.

**Architecture Pattern**: Follows [HireSense](https://github.com/Jaysuun01/HireSense) design with Protocol-based agent messaging and coordinator orchestration.

## Architecture

Three independent agents communicate via uAgents Protocol:

```
Frontend
   ↓ (HTTP POST /api/chat)
Coordinator Agent (port 8080) with REST endpoint
   ↓ (uAgents Protocol)
Scoping Agent (port 8001) ←→ Research Agent (port 8002)
```

### How It Works

1. **Frontend** sends HTTP POST to `/api/chat` on coordinator
2. **Coordinator** orchestrates via uAgents Protocol messaging:
   - Sends user message to Scoping Agent
   - Waits for scoping response
   - If requirements complete, automatically triggers Research Agent
   - Returns results to frontend
3. **Agents run as separate processes** and communicate via Protocol
4. **Deterministic addresses** from seed values (no manual configuration needed)

### Agents

#### 1. Scoping Agent (`agents/scoping_agent.py`)
- **Purpose**: Gathers user requirements through natural conversation
- **Port**: Dynamic (base_port + 1)
- **Protocol**: Listens for `ScopingRequest`, replies with `ScopingResponse`
- **Collects**:
  - Budget (min/max)
  - Bedrooms
  - Bathrooms
  - Location (Bay Area)
  - Additional preferences
- **LLM**: ASI:1 Mini via `llm_client.py`
- **State**: Maintains conversation history per session

#### 2. Research Agent (`agents/research_agent.py`)
- **Purpose**: Searches for properties matching requirements
- **Port**: Dynamic (base_port + 2)
- **Protocol**: Listens for `ResearchRequest`, replies with `ResearchResponse`
- **Search**: Tavily API targeting Zillow, Redfin, Realtor.com, Trulia, Homes.com
- **LLM**: ASI:1 Mini for extracting structured property data
- **Returns**: Array of `PropertyListing` objects

#### 3. Estate Coordinator (`main.py:EstateCoordinator`)
- **Purpose**: Orchestrates agent communication flow
- **Port**: Dynamic (base_port + 3)
- **Responsibilities**:
  - Manages agent addresses
  - Queues user messages
  - Handles scoping/research responses
  - Tracks completion per session
  - Provides result retrieval

## Project Structure

```
backend/
├── agents/
│   ├── __init__.py           # Agent exports
│   ├── models.py             # uAgents Models (message schemas)
│   ├── llm_client.py         # ASI:1 LLM API wrapper
│   ├── tavily_client.py      # Tavily search API wrapper
│   ├── scoping_agent.py      # Requirements gathering agent (Protocol)
│   └── research_agent.py     # Property search agent (Protocol)
├── main.py                   # Coordinator + run_estate_search_system()
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
└── README.md                 # This file
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```bash
# ASI:1 LLM API Configuration
ASI_API_KEY=your_asi1_api_key_here
ASI_API_URL=https://api.asi1.ai/v1/chat/completions
ASI_MODEL=asi1-mini

# Tavily Search API Configuration
TAVILY_API_KEY=your_tavily_api_key_here
```

### 3. Run the System

You need to run **3 separate processes** - one for each agent:

```bash
# Terminal 1 - Scoping Agent
python3 agents/scoping_agent.py

# Terminal 2 - Research Agent
python3 agents/research_agent.py

# Terminal 3 - Coordinator (with REST endpoint)
python3 main.py
```

The coordinator will be available at `http://localhost:8080/api/chat`.

## Usage Flow

### 1. Initial Request

The user sends a message to start the conversation:

```python
result = await run_estate_search_system(
    user_message="Hi, I'm looking for a house in San Francisco",
    session_id="user-abc"
)
```

### 2. Agent Coordination Flow

```
User Message
    ↓
Coordinator queues message
    ↓
Scoping Agent receives ScopingRequest
    ↓
Scoping Agent uses LLM to process conversation
    ↓
Scoping Agent sends ScopingResponse back
    ↓
Coordinator checks if requirements complete
    ↓ (if complete)
Coordinator sends ResearchRequest to Research Agent
    ↓
Research Agent queries Tavily for properties
    ↓
Research Agent uses LLM to parse results
    ↓
Research Agent sends ResearchResponse back
    ↓
Coordinator returns EstateSearchResult
```

### 3. Result Format

```python
EstateSearchResult(
    requirements=UserRequirements(
        budget_min=500000,
        budget_max=1200000,
        bedrooms=3,
        bathrooms=2,
        location="San Francisco",
        additional_info="good schools, quiet neighborhood"
    ),
    properties=[
        PropertyListing(
            address="123 Main St",
            city="San Francisco",
            price=950000,
            bedrooms=3,
            bathrooms=2,
            sqft=1800,
            description="Beautiful home...",
            url="https://zillow.com/..."
        ),
        # ... more properties
    ],
    search_summary="Found 5 properties matching your criteria...",
    session_id="user-abc"
)
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Agent Framework** | Fetch.ai uAgents | Multi-agent orchestration |
| **Agent Communication** | uAgents Protocols | Protocol-based messaging |
| **Coordinator Pattern** | EstateCoordinator Agent | Orchestrates agent flow |
| **LLM** | ASI:1 Mini | Natural conversation & data extraction |
| **Search** | Tavily API | Web search for property listings |
| **Data Models** | uagents.Model (Pydantic) | Type-safe message schemas |
| **Async** | aiohttp, asyncio | Asynchronous API calls |

## Design Decisions

### Why Protocol-based messaging?
- **True agent autonomy**: Agents communicate via uAgents native protocols
- **Decoupled architecture**: Each agent is independent and reusable
- **Scalable**: Easy to add more agents to the pipeline
- **Follows uAgents best practices**: Natural fit for multi-agent systems

### Why Coordinator Agent?
- **Central orchestration**: Single point of control for complex flows
- **State management**: Tracks multi-step conversations per session
- **Automatic flow**: Triggers research when scoping complete
- **Follows HireSense pattern**: Proven architecture for multi-agent systems

### Why ASI:1 Mini?
- **Optimized for agentic workflows**: Designed for multi-agent systems
- **Fast and cost-effective**: Quick responses for conversational flow
- **JSON mode support**: Reliable structured output parsing

### Why Tavily?
- **Real-time web search**: Up-to-date property listings
- **Domain filtering**: Target specific real estate sites
- **Advanced search depth**: Better quality results for property research

## Conversation Handling

The system supports **multi-turn conversations** for requirement gathering:

```python
# Turn 1
result1 = await run_estate_search_system(
    "Looking for a house",
    "session-1"
)
# Scoping agent asks for more details

# Turn 2
result2 = await run_estate_search_system(
    "3 bedrooms in Oakland, budget around $800k",
    "session-1"
)
# Scoping agent may ask about bathrooms/preferences

# Turn 3
result3 = await run_estate_search_system(
    "2 bathrooms, need good schools nearby",
    "session-1"
)
# Scoping complete, research triggered, properties returned
```

## Event Emitter (Optional)

Pass an event emitter callback for real-time updates:

```python
async def my_emitter(agent_name, message, event_type):
    print(f"[{agent_name}] {message}")
    # Send to WebSocket, log, etc.

result = await run_estate_search_system(
    user_message="...",
    session_id="...",
    event_emitter=my_emitter
)
```

## Development

### Running Individual Agents

For development/testing:

```bash
# This won't work standalone - agents need coordinator!
# Use main.py to run the full system
python main.py
```

### Adding New Agents

1. Create agent class inheriting from `Agent` in `agents/`
2. Define Protocol message handlers
3. Add models to `agents/models.py`
4. Update coordinator to include new agent in flow
5. Update `run_estate_search_system()` to instantiate new agent

### Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Frontend Integration

### Next.js API Route Example

```typescript
// app/api/estate-search/route.ts
import { spawn } from 'child_process';

export async function POST(req: Request) {
  const { message, sessionId } = await req.json();

  // Call Python backend
  const python = spawn('python3', [
    '-c',
    `
import asyncio
from main import run_estate_search_system
import json

result = asyncio.run(run_estate_search_system("${message}", "${sessionId}"))
print(json.dumps(result.dict() if result else None))
    `
  ]);

  let data = '';
  python.stdout.on('data', (chunk) => data += chunk);

  await new Promise((resolve) => python.on('close', resolve));

  return Response.json(JSON.parse(data));
}
```

Or use a proper Python API server (recommended).

## Future Enhancements

- [ ] Add WebSocket support for real-time conversation updates
- [ ] Deploy agents to Agentverse for hosted operation
- [ ] Add geocoding agent for accurate map coordinates
- [ ] Implement caching for repeated searches
- [ ] Add property comparison agent
- [ ] Integrate with real estate APIs for verified listings
- [ ] Add agent-to-agent negotiation for best matches

## Resources

- [uAgents Documentation](https://uagents.fetch.ai/docs)
- [uAgents Protocols Guide](https://uagents.fetch.ai/docs/guides/agents/intermediate/protocols)
- [HireSense Reference Architecture](https://github.com/Jaysuun01/HireSense)
- [ASI:1 API Documentation](https://docs.asi1.ai)
- [Tavily API Documentation](https://docs.tavily.com)

## License

MIT
