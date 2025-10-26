"""
ASI:1 Email Agent - Sends email confirmations using Fetch.ai chat protocol
"""
from datetime import datetime
from uuid import uuid4
from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
)
from agents.models import Model


class EmailRequest(Model):
    agent_address: str
    recipient_email: str
    subject: str
    content: str
    session_id: str


class EmailResponse(Model):
    status: str
    message: str
    session_id: str


def create_asi_email_agent(port: int = 8009) -> Agent:
    """
    Creates an ASI:1 email agent that communicates with the ASI:1 email service
    using the chat protocol.
    """
    agent = Agent(
        name="asi_email_agent",
        port=port,
        seed="asi_email_agent_seed",
        endpoint=[f"http://localhost:{port}/submit"]
    )

    # Create protocol compatible with chat protocol spec
    protocol = Protocol(spec=chat_protocol_spec)

    # Storage for responses
    email_responses = {}

    @agent.on_event("startup")
    async def startup(ctx: Context):
        ctx.logger.info("🤖 ASI:1 Email Agent started")
        ctx.logger.info(f"   Address: {ctx.agent.address}")

    @protocol.on_message(ChatMessage)
    async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
        """Handle responses from ASI:1 email agent"""
        ctx.logger.info(f"📩 Received chat message from {sender}")

        # Send acknowledgement
        await ctx.send(
            sender,
            ChatAcknowledgement(
                timestamp=datetime.now(),
                acknowledged_msg_id=msg.msg_id
            )
        )

        # Extract text content
        text = ''
        for item in msg.content:
            if isinstance(item, TextContent):
                text += item.text

        ctx.logger.info(f"   Message content: {text}")

        # Store response (you can correlate this with session IDs if needed)
        email_responses[sender] = text

    @protocol.on_message(ChatAcknowledgement)
    async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
        """Handle acknowledgements from ASI:1 agent"""
        ctx.logger.info(f"✅ Received acknowledgement from {sender} for message {msg.acknowledged_msg_id}")

    @agent.on_message(EmailRequest, replies=EmailResponse)
    async def handle_email_request(ctx: Context, sender: str, msg: EmailRequest):
        """
        Handle email request - sends a ChatMessage to the ASI:1 email agent
        """
        ctx.logger.info(f"📧 Email request received for session {msg.session_id}")
        ctx.logger.info(f"   Recipient: {msg.recipient_email}")
        ctx.logger.info(f"   Subject: {msg.subject}")
        ctx.logger.info(f"   ASI:1 Agent: {msg.agent_address}")

        try:
            # Format the email content for the ASI:1 agent
            email_text = f"""
Please send an email with the following details:

To: {msg.recipient_email}
Subject: {msg.subject}

Content:
{msg.content}
            """.strip()

            # Send ChatMessage to ASI:1 email agent
            await ctx.send(
                msg.agent_address,
                ChatMessage(
                    timestamp=datetime.now(),
                    msg_id=uuid4(),
                    content=[TextContent(type="text", text=email_text)]
                )
            )

            ctx.logger.info("✅ Email request sent to ASI:1 agent")

            await ctx.send(
                sender,
                EmailResponse(
                    status="success",
                    message="Email request sent to ASI:1 agent",
                    session_id=msg.session_id
                )
            )

        except Exception as e:
            ctx.logger.error(f"❌ Error sending email request: {e}")
            await ctx.send(
                sender,
                EmailResponse(
                    status="error",
                    message=str(e),
                    session_id=msg.session_id
                )
            )

    # Include the chat protocol
    agent.include(protocol, publish_manifest=True)

    return agent
