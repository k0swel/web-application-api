from dataclasses import dataclass
from datetime import datetime

@dataclass
class PostInfo():
    id: int
    title: str
    creation_date: datetime
    text: str
    images: list[str] # [{id, url}, {id, url}]
    author: str