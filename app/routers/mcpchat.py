from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.mcpchat import McpChat, McpChatCreate
from app.utils.openAI import openai_api
# from app.database.mcpchat_db import create_mcpchat, get_mcpchats_by_user

router = APIRouter(
    prefix="/api/mcpchat",
    tags=["mcpchat"]
)

# Mock function to simulate OpenAI API call
# def openai_api(content: str) -> str:
#     # Simulate a call to OpenAI API and return a response
#     # In a real application, you would replace this with actual API call
#     return f"Response to: {content}"

# Endpoint to create a new chat message
@router.post("/", response_model=McpChat)
async def create_mcpchat_endpoint(mcpchat: McpChatCreate):
    mcpchat_dict = mcpchat.dict()
    mcpchat_dict["reply"] = openai_api(mcpchat_dict["content"])
    return mcpchat_dict
    # mcpchat_dict["user_id"] = user_id  # Adding user_id to the request body
    # return await create_mcpchat(McpChatCreate(**mcpchat_dict))

# # Endpoint to get chat messages by user_id
# @router.get("/user/{user_id}", response_model=List[McpChat])
# async def get_mcpchats_by_user_endpoint(user_id: str):
#     mcpchats = await get_mcpchats_by_user(user_id)
#     if not mcpchats:
#         raise HTTPException(status_code=404, detail="No chats found for this user")
#     return mcpchats

# # Endpoint to create a new chat message for a specific user
# @router.post("/user", response_model=McpChat)
# async def create_mcpchat_endpoint(mcpchat: McpChatCreate):
#     mcpchat_dict = mcpchat.dict()
#     mcpchat_dict["reply"] = "hello world"
#     # mcpchat_dict["user_id"] = user_id  # Adding user_id to the request body
#     return await create_mcpchat(McpChatCreate(**mcpchat_dict))


