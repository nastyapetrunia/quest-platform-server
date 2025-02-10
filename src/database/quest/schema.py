from datetime import datetime
from typing import List, Optional, Union
from bson import ObjectId
from pydantic import BaseModel, Field, HttpUrl, ConfigDict

class QuizOption(BaseModel):
    """
    Schema for defining an option in a quiz question.

    Attributes:
    - text: The text of the option.
    - id: Unique identifier for the option.
    """
    text: str = Field(..., description="The text of the quiz option")
    id: str = Field(..., description="Unique identifier for the quiz option")


class QuizLevel(BaseModel):
    """
    Schema for a quiz level in a quest.

    Attributes:
    - type: The type of the level, typically 'quiz'.
    - id: Unique identifier for the quiz level.
    - name: Name or title of the quiz level.
    - question: The quiz question text.
    - pictureUrls: A list of URLs for images associated with the question.
    - options: A list of possible options for the quiz.
    - correctOptionId: The ID of the correct answer.
    """
    type: str = Field("quiz", description="The type of the level")
    id: str = Field(..., description="Unique identifier for the quiz level")
    name: str = Field(..., description="Name or title of the quiz level")
    question: str = Field(..., description="The question text for the quiz")
    picture_urls: List[HttpUrl] = Field(..., description="List of URLs for images related to the question")
    options: Optional[List[QuizOption]] = Field(..., description="List of options for the quiz question")
    correct_option_id: Optional[str] = Field(..., description="The ID of the correct quiz option")


class InputLevel(BaseModel):
    """
    Schema for an input type level in a quest.

    Attributes:
    - type: The type of the level, typically 'input'.
    - id: Unique identifier for the input level.
    - name: Name or title of the input level.
    - question: The question text for the input level.
    - pictureUrls: A list of URLs for images associated with the question.
    - tryLimit: The number of attempts allowed for the input level.
    """
    type: str = Field("input", description="The type of the level")
    id: str = Field(..., description="Unique identifier for the input level")
    name: str = Field(..., description="Name or title of the input level")
    question: str = Field(..., description="The question text for the input level")
    picture_urls: List[HttpUrl] = Field(..., description="List of URLs for images related to the question")
    try_limit: Optional[int] = Field(..., description="The number of attempts allowed for the input level")


class CreateQuest(BaseModel):
    """
    Schema for creating a new quest.

    Attributes:
    - name: The name of the quest.
    - title: A title of the quest.
    - description: A description of the quest.
    - time_limit: The time limit for completing the quest (in minutes).
    - created_at: Timestamp of when the quest was created.
    - difficulty: The difficulty level of the quest (e.g., 'easy', 'medium', 'hard').
    - main_picture: URL for the main picture of the quest.
    - created_by: ObjectId of the user who created the quest.
    - levels: A list of levels (input or quiz) for the quest.
    """
    name: str = Field(..., description="Name of the quest")
    title: str = Field(..., description="Title of the quest")
    description: str = Field(..., description="Description of the quest")
    time_limit: int = Field(..., description="Time limit for completing the quest (in minutes)")
    created_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), description="Timestamp of when the quest was created")
    difficulty: str = Field(..., description="The difficulty level of the quest")
    main_picture: Optional[HttpUrl] = Field(..., description="URL of the main picture for the quest")
    created_by: ObjectId = Field(..., description="ObjectId of the user who created the quest")
    levels: List[Union[InputLevel, QuizLevel]] = Field(default_factory=list, description="A list of levels in the quest (can be input or quiz levels)")

    model_config = ConfigDict(
        extra='forbid',
        arbitrary_types_allowed=True
    )


class UpdateQuest(BaseModel):
    """
    Schema for updating an existing quest.

    Attributes:
    - id: The unique ObjectId of the quest.
    - name: The name of the quest.
    - description: A description of the quest.
    - time_limit: The time limit for completing the quest (in seconds).
    - difficulty: The difficulty level of the quest (e.g., 'easy', 'medium', 'hard').
    - main_picture: URL for the main picture of the quest.
    - levels: A list of levels (input or quiz) for the quest.
    """
    id: ObjectId = Field(..., description="Unique ObjectId of the quest", alias="_id")
    name: Optional[str] = Field(..., description="Name of the quest")
    description: Optional[str] = Field(..., description="Description of the quest")
    time_limit: Optional[int] = Field(..., description="Time limit for completing the quest (in seconds)")
    difficulty: Optional[str] = Field(..., description="The difficulty level of the quest")
    main_picture: Optional[Union[HttpUrl, None]] = Field(..., description="URL of the main picture for the quest")
    levels: Optional[List[Union[InputLevel, QuizLevel]]] = Field(default_factory=list, description="A list of levels in the quest (can be input or quiz levels)")

    model_config = ConfigDict(
        extra='forbid',
        arbitrary_types_allowed=True
    )
