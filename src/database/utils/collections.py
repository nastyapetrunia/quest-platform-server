from enum import Enum
from collections import namedtuple

from src.database.user.schema import User


CollectionMetadata = namedtuple("CollectionMetadata", ["name", "validation_schema"])

class Collections(Enum):

    USER = CollectionMetadata(
        name='Users',
        validation_schema=User,
    )
