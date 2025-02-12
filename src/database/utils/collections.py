from enum import Enum
from collections import namedtuple

from src.database.user.schema import CreateUser, UpdateUser
from src.database.quest.schema import CreateQuest, UpdateQuest


CollectionMetadata = namedtuple("CollectionMetadata", ["name", "validation_schema_create", "validation_schema_update"])

class Collections(Enum):

    USER = CollectionMetadata(
        name='Users',
        validation_schema_create=CreateUser,
        validation_schema_update=UpdateUser,
    )
    QUEST = CollectionMetadata(
        name='Quests',
        validation_schema_create=CreateQuest,
        validation_schema_update=UpdateQuest,
    )