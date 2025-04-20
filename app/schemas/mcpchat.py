from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId
from datetime import datetime

# 
class McpChatBase(BaseModel):
    datetime: datetime
    content: str
    # user_id: str
    
    # user_id: str

class McpChatCreate(McpChatBase):
    pass

class McpChat(McpChatBase):

    # id: str = Field(alias="_id")
    reply: str

    class Config:
        #json_encoders = {ObjectId: str}
        populate_by_name = True
