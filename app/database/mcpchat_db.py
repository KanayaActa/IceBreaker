# from datetime import datetime
# from typing import List
# from bson import ObjectId
# from app.database.connection import get_database
# from app.schemas.mcpchat import McpChat, McpChatCreate

# # Fetching the collection
# async def get_collection():
#     db = await get_database()
#     return db["mcpchat"]

# # Creating a new chat message
# async def create_mcpchat(mcpchat: McpChatCreate) -> McpChat:
#     collection = await get_collection()
#     mcpchat_dict = mcpchat.dict()
#     mcpchat_dict["datetime"] = datetime.utcnow()  # Use UTC time to avoid timezone issues
#     result = await collection.insert_one(mcpchat_dict)
#     created_mcpchat = await collection.find_one({"_id": result.inserted_id})
#     created_mcpchat["_id"] = str(created_mcpchat["_id"])  # Convert ObjectId to string
#     return McpChat(**created_mcpchat)

# # Fetching chats by user_id
# async def get_mcpchats_by_user(user_id: str) -> List[McpChat]:
#     collection = await get_collection()
#     mcpchats = []
#     # Efficiently fetch documents and append them as McpChat instances
#     async for mcpchat in collection.find({"user_id": user_id}):
#         mcpchats.append(McpChat(**mcpchat))
#     return mcpchats
