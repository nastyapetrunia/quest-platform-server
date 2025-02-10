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
    - picture_urls: A list of URLs for images associated with the question.
    - options: A list of possible options for the quiz.
    - correct_option_id: The ID of the correct answer.
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
    - picture_urls: A list of URLs for images associated with the question.
    - try_limit: The number of attempts allowed for the input level.
    """
    type: str = Field("input", description="The type of the level")
    id: str = Field(..., description="Unique identifier for the input level")
    name: str = Field(..., description="Name or title of the input level")
    question: str = Field(..., description="The question text for the input level")
    picture_urls: List[HttpUrl] = Field(..., description="List of URLs for images related to the question")
    try_limit: Optional[int] = Field(..., description="The number of attempts allowed for the input level")

class QuestRating(BaseModel):
    """
    Schema for defining a user's rating of a quest.

    Attributes:
    - review (Optional[str]): The text of the user's review for the quest. Can be omitted.
    - user_id (ObjectId): The unique identifier of the user who provided the rating.
    - rating (int): The numerical rating given by the user.
    """

    review: Optional[str] = Field(None, description="Optional text review of the quest")
    user_id: ObjectId = Field(..., description="Unique ObjectId of the user who rated the quest")
    rating: int = Field(..., description="Numeric rating given by the user (e.g., 1 to 5)")

    model_config = ConfigDict(
        extra='forbid',
        arbitrary_types_allowed=True
    )

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
    ratings: List[QuestRating] = Field(default_factory=list, description="A list of user ratings of the quiz")
    times_played: int = Field(default=0, description="Number of times the quest has been played")
    avg_rating: float = Field(default=0.0, description="Average rating of the quest, calculated from user ratings")

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
    ratings: Optional[List[QuestRating]] = Field(default_factory=list, description="A list of user ratings of the quest")
    times_played: Optional[int] = Field(description="Number of times the quest has been played")
    avg_rating: Optional[float] = Field(default=0.0, description="Average rating of the quest, calculated from user ratings")

    model_config = ConfigDict(
        extra='forbid',
        arbitrary_types_allowed=True
    )
