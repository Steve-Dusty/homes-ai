"""
Prober Agent - Gathers intelligence about properties for negotiation leverage
============================================================================

This agent combines Tavily (for finding relevant sources) and BrightData (for scraping)
to gather information that can be used in negotiations. The LLM handles analysis.

Categories of intelligence:
- Time on market (longer = more desperate seller)
- Price history (reductions indicate flexibility)
- Property issues (repairs, violations, permits)
- Owner situation (foreclosure, estate sale, divorce, etc.)
- Market conditions (buyer's vs seller's market)
"""

from uagents import Agent, Context
from .models import ProberRequest, ProberResponse, ProberFinding
from .tavily_client import TavilyClient
from .brightdata_client import BrightDataClient
from .llm_client import SimpleLLMAgent


class ProberLLMAgent(SimpleLLMAgent):
    """LLM agent specialized for analyzing property intelligence and extracting negotiation leverage"""

    def __init__(self):
        system_prompt = """You are a real estate negotiation analyst. Extract actionable intelligence from property data.
Return ONLY valid JSON, no markdown formatting or additional text."""
        super().__init__(name="ProberLLM", system_prompt=system_prompt)

    async def analyze_property_intel(self, address: str, scraped_content: list) -> dict:
        """
        Analyze scraped property content and extract negotiation leverage.
        Returns structured findings.
        """
        # Format scraped content for LLM
        content_summary = ""
        for idx, item in enumerate(scraped_content, 1):
            url = item.get("url", "Unknown")
            text = item.get("content", "")[:2000]  # Limit to first 2000 chars per source
            content_summary += f"\n\n--- Source {idx}: {url} ---\n{text}\n"

        prompt = f"""Analyze the following information about a property to find leverage points for negotiation.

Property Address: {address}

Scraped Information:
{content_summary}

Extract negotiation leverage in the following categories:
1. **time_on_market**: How long has it been listed? Price reductions?
2. **price_history**: Previous sale prices, listing price changes
3. **property_issues**: Repairs needed, violations, permits, problems
4. **owner_situation**: Foreclosure, estate sale, divorce, relocation, financial distress
5. **market_conditions**: Is it a buyer's or seller's market? Days on market trends?

For each finding, provide:
- category (one of the above)
- summary (1-2 sentences)
- leverage_score (0-10, how useful for negotiation)
- details (more context)
- source_url (if applicable)

Also provide:
- overall_assessment: A 2-3 sentence summary of the buyer's negotiation position
- leverage_score: Overall score 0-10 (10 = strong buyer leverage)

Return ONLY valid JSON in this exact format:
{{
  "findings": [
    {{
      "category": "time_on_market",
      "summary": "...",
      "leverage_score": 7.5,
      "details": "...",
      "source_url": "..."
    }}
  ],
  "overall_assessment": "...",
  "leverage_score": 6.5
}}

If you cannot find any information, return an empty findings array and low leverage_score.
"""

        result = await self.query_with_json(prompt, temperature=0.3)

        if result["success"]:
            return result["data"]
        else:
            return {
                "findings": [],
                "overall_assessment": f"Analysis failed: {result.get('error', 'Unknown error')}",
                "leverage_score": 0.0
            }


def create_prober_agent(port: int = 8006):
    agent = Agent(
        name="prober_agent",
        port=port,
        seed="prober_agent_seed",
        endpoint=[f"http://localhost:{port}/submit"],
    )

    tavily = TavilyClient()
    brightdata = BrightDataClient()
    llm_agent = ProberLLMAgent()

    @agent.on_event("startup")
    async def startup(ctx: Context):
        ctx.logger.info(f"Prober Agent started at {ctx.agent.address}")

    @agent.on_message(model=ProberRequest)
    async def handle_probe_request(ctx: Context, sender: str, msg: ProberRequest):
        ctx.logger.info(f"Probing property: {msg.address}")

        # Step 1: Use Tavily to find relevant sources about this property
        search_queries = [
            f"{msg.address} property history sale price",
            f"{msg.address} zillow redfin listing",
            f"{msg.address} days on market price reduction",
        ]

        all_urls = []
        for query in search_queries:
            ctx.logger.info(f"Tavily search: {query}")
            tavily_result = await tavily.search(
                query=query,
                search_depth="advanced",
                max_results=3
            )

            if tavily_result.get("success"):
                results = tavily_result.get("results", [])
                for result in results:
                    url = result.get("url")
                    if url and url not in [u["url"] for u in all_urls]:
                        all_urls.append({
                            "url": url,
                            "title": result.get("title", ""),
                            "content": result.get("content", "")
                        })
            else:
                ctx.logger.warning(f"Tavily search failed: {tavily_result.get('error')}")

        ctx.logger.info(f"Found {len(all_urls)} unique URLs from Tavily")

        # Step 2: Use BrightData to scrape the top URLs (limit to 5 to avoid rate limits)
        scraped_content = []
        urls_to_scrape = all_urls[:5]

        for item in urls_to_scrape:
            url = item["url"]
            ctx.logger.info(f"Scraping with BrightData: {url}")

            try:
                scrape_result = await brightdata.call(
                    "scrape_as_markdown",
                    {"url": url}
                )

                if scrape_result.get("success"):
                    markdown_content = scrape_result.get("output", "")
                    scraped_content.append({
                        "url": url,
                        "title": item["title"],
                        "content": markdown_content,
                        "tavily_snippet": item["content"]  # Keep Tavily's snippet too
                    })
                    ctx.logger.info(f"Successfully scraped {url}")
                else:
                    ctx.logger.warning(f"BrightData scrape failed for {url}: {scrape_result.get('error')}")
                    # Fall back to Tavily content
                    scraped_content.append({
                        "url": url,
                        "title": item["title"],
                        "content": item["content"],
                        "tavily_snippet": item["content"]
                    })
            except Exception as e:
                ctx.logger.warning(f"Error scraping {url}: {e}")
                # Fall back to Tavily content
                scraped_content.append({
                    "url": url,
                    "title": item["title"],
                    "content": item["content"],
                    "tavily_snippet": item["content"]
                })

        ctx.logger.info(f"Scraped {len(scraped_content)} sources")

        # Step 3: Use LLM to analyze and extract negotiation leverage
        ctx.logger.info("Analyzing content with LLM...")
        analysis = await llm_agent.analyze_property_intel(msg.address, scraped_content)

        # Convert findings to ProberFinding models
        findings = []
        for finding_dict in analysis.get("findings", []):
            try:
                findings.append(ProberFinding(
                    category=finding_dict.get("category", "unknown"),
                    summary=finding_dict.get("summary", ""),
                    leverage_score=float(finding_dict.get("leverage_score", 0.0)),
                    details=finding_dict.get("details", ""),
                    source_url=finding_dict.get("source_url")
                ))
            except Exception as e:
                ctx.logger.warning(f"Failed to create ProberFinding: {e}")
                continue

        ctx.logger.info(f"Extracted {len(findings)} findings with overall leverage score: {analysis.get('leverage_score', 0.0)}")

        # Send response
        await ctx.send(sender, ProberResponse(
            address=msg.address,
            findings=findings,
            overall_assessment=analysis.get("overall_assessment", "No assessment available"),
            leverage_score=float(analysis.get("leverage_score", 0.0)),
            session_id=msg.session_id
        ))

    return agent
