
import asyncio
from app.services.pinecone_service import pinecone_service


async def get_data():
    data = await pinecone_service.search_creators(
        query={
        "inputs": {"text": "Lifestyle"}, 
        "top_k": 2
    }
        )
    print(data)



async def put_data():
    creator_id = 12345 
    creator_data = {
        'creator_id': creator_id,
        'full_name': "Om",
        'category': "Lifestyle",
        'location': "India",
        'instagram_followers': "1000",
        'base_rate': "10000",
        'engagement_rate': "1000"
    }
    print(creator_data)
    done = await pinecone_service.upsert_creator(creator_id, creator_data)
    print(done)

    

asyncio.run(put_data())
asyncio.run(get_data())