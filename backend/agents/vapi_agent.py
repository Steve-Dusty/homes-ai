"""
Vapi Agent - Handles AI phone call negotiations with listing agents
====================================================================

This agent:
1. Takes property intelligence from prober agent
2. Builds a system prompt with all the leverage data
3. Updates the Vapi assistant with the prompt
4. Initiates a phone call to the listing agent
"""

from uagents import Agent, Context
from .models import Model
from typing import Optional, Dict, Any, List
from .vapi_client import VapiClient
import os
import json


# Vapi Models for uAgents
class VapiRequest(Model):
    """Request to make a negotiation call via Vapi"""
    property_address: str
    user_name: str
    user_email: str
    user_preferences: str
    intelligence: Dict[str, Any]  # The full intelligence JSON from prober
    session_id: str


class VapiResponse(Model):
    """Response from Vapi agent"""
    call_id: Optional[str] = None
    status: str
    message: str
    session_id: str


def build_system_prompt(vapi_context: Dict[str, Any]) -> str:
    """Build the system prompt for Vapi assistant with intelligence data"""

    property_addr = vapi_context['property']['address']
    user_name = vapi_context['user']['name']
    user_prefs = vapi_context['user']['preferences']
    leverage_score = vapi_context['intelligence']['leverage_score']
    assessment = vapi_context['intelligence']['overall_assessment']
    findings = vapi_context['intelligence']['findings']

    # Format findings for the prompt
    findings_text = ""
    for idx, finding in enumerate(findings, 1):
        findings_text += f"""
{idx}. {finding['category'].upper().replace('_', ' ')} (Leverage Score: {finding['leverage_score']}/10)
   - Summary: {finding['summary']}
   - Details: {finding['details']}
"""
        if finding.get('source_url'):
            findings_text += f"   - Source: {finding['source_url']}\n"

    system_prompt = f"""You are an AI negotiation agent representing the buyer {user_name} for the property at {property_addr}.

You are on a PHONE CALL with the listing agent to negotiate a better price. Your goal is to use the intelligence data below to get the LOWEST possible price for your client.

====================
BUYER INFORMATION
====================
Name: {user_name}
Preferences: {user_prefs}

====================
PROPERTY INTELLIGENCE
====================
Overall Leverage Score: {leverage_score}/10 (higher = more buyer leverage)

Overall Assessment:
{assessment}

Key Findings (USE THESE AS LEVERAGE):
{findings_text}

====================
NEGOTIATION STRATEGY
====================

1. OPENING:
   - Identify yourself as representing {user_name}
   - Express serious interest in the property
   - Mention you've done thorough market research

2. PRESENT CONCERNS (use the findings above):
   - Reference specific data points from findings
   - Focus on HIGH leverage score items first (8+ scores)
   - Be specific with numbers (days on market, price reductions, etc.)
   - Frame as "market analysis" not criticism

3. REQUEST PRICE REDUCTION:
   - Based on the leverage score and findings, suggest a price adjustment
   - If leverage score is 7-10: Request 5-10% reduction
   - If leverage score is 5-7: Request 3-5% reduction
   - If leverage score is 3-5: Request 1-3% reduction
   - Justify with specific findings

4. HANDLE OBJECTIONS:
   - If they dispute findings, ask for their counter-data
   - Emphasize your client's serious interest and ability to close
   - Reference buyer's preferences: {user_prefs}
   - Stay professional but persistent

5. CLOSING:
   - Try to get verbal agreement on adjusted price
   - Offer to submit formal offer immediately
   - Get next steps (inspection, paperwork, etc.)

====================
RULES (MUST FOLLOW)
====================
- Keep responses BRIEF (under 75 words per turn)
- Be conversational and natural (you're on a phone call)
- Use ONLY the intelligence data provided - do NOT fabricate facts
- Stay professional and respectful
- Focus on DATA and MARKET CONDITIONS, not personal attacks
- Follow Fair Housing laws - no discriminatory language
- Do NOT use emojis or special formatting

====================
EXAMPLE OPENING
====================
"Hi, this is calling on behalf of {user_name} regarding the property at {property_addr}. We're very interested, but our market analysis has identified some concerns we'd like to discuss. Do you have a moment to talk about the pricing?"

====================
KEY TALKING POINTS
====================
Based on your intelligence, emphasize:
{chr(10).join([f"- {f['summary']}" for f in findings[:3]])}

Remember: Your job is to get the LOWEST price possible while being professional. Use the intelligence data strategically!
"""

    return system_prompt.strip()


def create_vapi_agent(port: int = 8008):
    agent = Agent(
        name="vapi_agent",
        port=port,
        seed="vapi_agent_seed",
        endpoint=[f"http://localhost:{port}/submit"],
    )

    # Initialize Vapi client
    target_phone_number = "+18587331359"  # Listing agent phone number

    try:
        vapi_client = VapiClient()
    except Exception as e:
        print(f"⚠️ WARNING: Failed to initialize Vapi client: {e}")
        vapi_client = None

    @agent.on_event("startup")
    async def startup(ctx: Context):
        ctx.logger.info(f"Vapi Agent started at {ctx.agent.address}")
        ctx.logger.info(f"Target phone: {target_phone_number}")

    @agent.on_message(model=VapiRequest)
    async def handle_vapi_request(ctx: Context, sender: str, msg: VapiRequest):
        ctx.logger.info(f"📞 Vapi call request for: {msg.property_address}")
        ctx.logger.info(f"   User: {msg.user_name}")
        ctx.logger.info(f"   Leverage Score: {msg.intelligence.get('leverage_score', 0)}/10")

        if not vapi_client:
            ctx.logger.error("❌ Vapi client not initialized (missing API key)")
            await ctx.send(sender, VapiResponse(
                call_id=None,
                status="error",
                message="Vapi API key not configured",
                session_id=msg.session_id
            ))
            return

        try:
            # Build full context for system prompt
            vapi_context = {
                "property": {
                    "address": msg.property_address
                },
                "user": {
                    "name": msg.user_name,
                    "email": msg.user_email,
                    "preferences": msg.user_preferences
                },
                "intelligence": msg.intelligence
            }

            # Build system prompt with all intelligence
            ctx.logger.info("🔧 Building system prompt with intelligence data...")
            system_prompt = build_system_prompt(vapi_context)

            # Build first message
            first_message = f"Hi, I'm calling on behalf of {msg.user_name} regarding the property at {msg.property_address}. We're very interested and have done some market research. Do you have a moment to discuss?"

            # Update Vapi assistant with new system prompt
            ctx.logger.info(f"📝 Updating Vapi assistant...")
            success = vapi_client.update_assistant(
                system_prompt=system_prompt,
                first_message=first_message
            )

            if not success:
                raise Exception("Failed to update Vapi assistant")

            ctx.logger.info("✅ Assistant updated successfully")

            # Make the phone call
            ctx.logger.info(f"📞 Initiating call to {target_phone_number}...")
            call_id = vapi_client.create_call(customer_phone=target_phone_number)

            if not call_id:
                raise Exception("Failed to create call")

            ctx.logger.info(f"✅ Call initiated! Call ID: {call_id}")

            # Send success response
            await ctx.send(sender, VapiResponse(
                call_id=call_id,
                status="success",
                message=f"Negotiation call initiated to {target_phone_number}",
                session_id=msg.session_id
            ))

        except Exception as e:
            ctx.logger.error(f"❌ Vapi call failed: {e}")
            import traceback
            traceback.print_exc()

            await ctx.send(sender, VapiResponse(
                call_id=None,
                status="error",
                message=f"Failed to initiate call: {str(e)}",
                session_id=msg.session_id
            ))

    return agent
