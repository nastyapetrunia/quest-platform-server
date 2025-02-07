from datetime import datetime
from typing import List, Optional, Union
from bson import ObjectId
from pydantic import BaseModel, Field, HttpUrl, ConfigDict

class QuestHistory(BaseModel):
    """
    Schema for validating quest history entries.

    Attributes:
    - quest_id: Unique identifier for the quest
    - score: Score the user achieved or None if not finished
    - completed: Boolean indicating if the quest was completed
    - time_spent: Time spent on the quest (in seconds or any unit)
    - rating: Rating the user gave to the quest (if any)
    - attempted_at: Timestamp for when the quest was attempted
    """
    quest_id: str  # Quest ID or reference to the quest
    score: Optional[int] = None  # Score or None if not finished
    completed: bool = False  # Whether the quest was completed
    time_spent: Optional[float] = None  # Time spent on the quest (in seconds or any unit)
    rating: Optional[int] = None  # Rating the user gave to the quest (if any)
    attempted_at: datetime  # Timestamp for when the quest was attempted

class User(BaseModel):
    """
    Schema for validating user documents.

    Attributes:
    - created_at: Timestamp indicating when the user was created.
    - name: User's name
    - email: User's email address
    - profile_picture: URL to the user's profile picture (S3 URL)
    - created_quests: List of quest IDs the user has created
    - quest_history: List of quests attempted by the user (with score, rating, and completion status)

    Config:
        extra (str): Specifies that no additional fields are allowed in the schema.
    """
    name: str = Field(..., description="User name")
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password hash")
    created_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), description="Timestamp of account creation")
    profile_picture: Union[HttpUrl, None] = Field(..., description="User profile picture S3 url")
    created_quests: List[ObjectId] = Field(default_factory=list, description="List of quests created by the user")
    quest_history: List[QuestHistory] = Field(default_factory=list, description="History of quests attempted by the user")

    model_config = ConfigDict(
        extra='forbid',
        arbitrary_types_allowed=True
    )