# assistant_outreach_service/main.py

from fastapi import FastAPI, HTTPException
import requests
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI
import os
import asyncpg

# Load environment variables (replace with actual values or load from .env)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
client = OpenAI(api_key=OPENAI_API_KEY,default_headers={"OpenAI-Beta": "assistants=v2"})

app = FastAPI()

# PostgreSQL connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://username:password@localhost:5432/db")

functions=[
  {
    "name": "update_outreach_status",
    "description": "Update the status of outreach lifecycle in the database",
    "strict": True,
    "parameters": {
      "type": "object",
      "properties": {
        "creator_id": {"type": "string"},
        "campaign_id": {"type": "string"},
        "status": {
          "type": "string",
          "enum": ["faq_answered", "negotiation_started", "price_agreed", "deal_closed"]
        },
        "final_price": {"type": "number"},
        "deliverables": {"type": "string"},
        "timeline": {"type": "string"}
      },
      "required": ["creator_id", "campaign_id", "status"]
    }
  }
]

class WhatsAppMessage(BaseModel):
    mobile_number: str
    message: str


class Creator(BaseModel):
    id: str
    name: str
    handle: str
    language: str
    mobile: str


class Campaign(BaseModel):
    id: int
    title: str
    description: str
    budget: float


@app.on_event("startup")
async def startup():
    app.state.db = await asyncpg.create_pool(DATABASE_URL)


@app.on_event("shutdown")
async def shutdown():
    await app.state.db.close()


async def get_creator_by_mobile(mobile):
    row = await app.state.db.fetchrow(
        f"""
        select 
	outreach_logs.*,
    campaign_creators.*,
    creators.*,
    campaigns.*,
    campaign_creators.status as creator_status
from 
	outreach_logs
left join 
	campaign_creators
ON
	campaign_creators.id = outreach_logs.campaign_creator_id
left join
	creators
ON
	creators.id = campaign_creators.creator_id
left join
	campaigns
ON
	campaigns.id = campaign_creators.campaign_id
WHERE
	outreach_logs.outreach_type = 'WHATSAPP'
AND
	campaign_creators.status IN ('ACCEPTED', 'INVITED', 'IN_PROGRESS')
AND
	outreach_logs.recipient_contact = '{mobile}'
limit 1
        """
    )
    print(f"Fetched creator data: {row} for mobile {mobile}")
    return row


async def create_thread_if_not_exist(creator_id, campaign_id):
    row = await app.state.db.fetchrow("SELECT thread_id FROM campaign_creators WHERE creator_id=$1 AND campaign_id=$2", creator_id, campaign_id)
    if row:
        return row["thread_id"]

    thread = client.beta.threads.create()

    await app.state.db.execute(
        "UPDATE campaign_creators SET thread_id=$3 WHERE creator_id=$1 AND campaign_id=$2",
        creator_id, campaign_id, thread.id
    )
    return thread.id


@app.post("/whatsapp-webhook")
async def handle_whatsapp_message(payload: WhatsAppMessage):
    creator_data = await get_creator_by_mobile(payload.mobile_number)

    if not creator_data:
        raise HTTPException(status_code=404, detail="Creator or campaign not found")

    # creator = Creator(**{k: creator_data[k] for k in Creator.__fields__})
    # campaign = Campaign(
    #     id=creator_data["campaign_id"],
    #     title=creator_data["title"],
    #     description=creator_data["description"],
    #     budget=creator_data["budget"]
    # )

    thread_id = await create_thread_if_not_exist(creator_data['creator_id'], creator_data['campaign_id'])

    # Post creator message to thread
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=payload.message
    )

    # Run the assistant on this thread
    run = client.beta.threads.runs.create(
        assistant_id=creator_data["assistant_id"],
        thread_id=thread_id
    )

    # Wait or poll run status until complete (simplified here)
    import time
    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        if run_status.status == "completed":
            break
        elif run_status.status == "failed":
            raise HTTPException(status_code=500, detail="Run failed")
        time.sleep(1)

    messages = client.beta.threads.messages.list(thread_id=thread_id)
    last_message = next((m for m in messages.data if m.role == "assistant"), None)
    response_text = last_message.content[0].text.value if last_message else "Sorry, I couldn't process that."

    return {"reply": response_text}


@app.post("/create-campaign-assistant")
async def create_campaign_assistant(campaign: Campaign):
    system_prompt = f"""
    You are an outreach agent for the campaign "{campaign.title}".
    Campaign Description: {campaign.description}
    Budget: {campaign.budget}
    Answer questions, negotiate prices within the budget, and close deals with creators.
    """

    assistant = requests.post("https://api.openai.com/v1/assistants",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
            "OpenAI-Beta": "assistants=v2"
        },
        json={
            "name" :f"Assistant for {campaign.title}",
            "instructions" : system_prompt,
            "tools" : [{"type": "function", "function": functions[0]}],  # Pass the function directly, not the array
            "model" : "gpt-3.5-turbo"
        }
    )
    assistant = assistant.json()
    print(assistant)
    await app.state.db.execute(
        "UPDATE campaigns SET assistant_id=$1 WHERE id=$2",
        assistant.get("id"), campaign.id
    )

    return {"assistant_id": assistant.get("id")}
