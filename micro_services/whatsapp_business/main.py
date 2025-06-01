# assistant_outreach_service/main.py

from fastapi import FastAPI, HTTPException, Request
import requests
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI
import os
import asyncpg
from app.config import settings
# Load environment variables (replace with actual values or load from .env)

client = OpenAI(api_key=settings.OPENAI_API_KEY,default_headers={"OpenAI-Beta": "assistants=v2"})

app = FastAPI()

# PostgreSQL connection
CHAT_DATABASE_URL = os.getenv("CHAT_DATABASE_URL")

functions=[
  {
    "name": "update_outreach_status",
    "description": "Update the status of outreach lifecycle in the database",
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
    app.state.db = await asyncpg.create_pool(settings.CHAT_DATABASE_URL)


@app.on_event("shutdown")
async def shutdown():
    await app.state.db.close()

from app.config import settings


def send_whatsapp_message(to_number: str, message: str):
    url = f"{settings.WHATSAPP_API_URL}"
    headers = {"Authorization": f"Bearer {settings.WHATSAPP_AGENT_API_TOKEN}"}
    data = {
        "messaging_product":"whatsapp",
        
        "to": to_number,

        "recipient_type": "individual",

        "type": "text",

        "text": {"body": message}

    }
    requests.post(url, json=data, headers=headers)
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
    if row['thread_id']:
        print(f"Thread already exists for creator {creator_id} and campaign {campaign_id}: {row['thread_id']}")
        return row["thread_id"]

    thread_response = requests.post("https://api.openai.com/v1/threads",
        headers={
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
            "OpenAI-Beta": "assistants=v2"
        }
    )
    thread = thread_response.json()
    print(f"Created new thread: {thread}")
    await app.state.db.execute(
        "UPDATE campaign_creators SET thread_id=$3 WHERE creator_id=$1 AND campaign_id=$2",
        creator_id, campaign_id, thread["id"]
    )
    return thread["id"]


@app.post("/whatsapp-webhook")
async def handle_whatsapp_message(payload: WhatsAppMessage):
    creator_data = await get_creator_by_mobile(payload.mobile_number)

    if not creator_data:
        raise HTTPException(status_code=404, detail="Creator or campaign not found")


    thread_id = await create_thread_if_not_exist(creator_data['creator_id'], creator_data['campaign_id'])

    # Post creator message to thread
    message_response = requests.post(f"https://api.openai.com/v1/threads/{thread_id}/messages",
        headers={
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
            "OpenAI-Beta": "assistants=v2"
        },
        json={
            "role": "user",
            "content": payload.message
        }
    )

    # Run the assistant on this thread
    run_response = requests.post(f"https://api.openai.com/v1/threads/{thread_id}/runs",
        headers={
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
            "OpenAI-Beta": "assistants=v2"
        },
        json={
            "assistant_id": creator_data["assistant_id"]
        }
    )
    run = run_response.json()
    print(f"Run started: {run}")
    # Wait or poll run status until complete (simplified here)
    import time
    while True:
        run_status_response = requests.get(f"https://api.openai.com/v1/threads/{thread_id}/runs/{run['id']}",
            headers={
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "OpenAI-Beta": "assistants=v2"
            }
        )
        run_status = run_status_response.json()
        if run_status["status"] == "completed":
            break
        elif run_status["status"] == "failed":
            raise HTTPException(status_code=500, detail="Run failed")
        time.sleep(1)

    messages_response = requests.get(f"https://api.openai.com/v1/threads/{thread_id}/messages",
        headers={
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "OpenAI-Beta": "assistants=v2"
        }
    )
    messages = messages_response.json()
    
    # Find the last assistant message
    last_message = None
    for message in messages["data"]:
        if message["role"] == "assistant":
            last_message = message
            break
    
    if last_message and last_message["content"]:
        response_text = last_message["content"][0]["text"]["value"]
    else:
        response_text = "Sorry, I couldn't process that."
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
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
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
@app.get("/newbothook")
async def setwebhook(request: Request):
    return request.query_params.get("challange")

@app.post("/whatsapp_bothook")
async def webhook(request: Request):
    data = await request.json()
    print(data)
    try:
        msgpayload=data.get("entry")[0].get("changes")[0].get("value").get("messages")[0]
    except:
        return {"status":"ignored"}
    if msgpayload.get("type")=="text":
        message = msgpayload.get("text").get("body")
        contact_number=msgpayload.get("from")
        response_txt = requests.post("http://localhost:8001/whatsapp-webhook",json={
            "message": message,
            "mobile_number": contact_number
        })
        await send_whatsapp_message(msgpayload.get("from"), response_txt.json().get("reply"))