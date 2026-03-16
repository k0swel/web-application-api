from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class PostInfo():
    id: int
    title: str
    creation_date: datetime
    text: str
    images: list[str] # [{id, url}, {id, url}]
    author: str

@dataclass
class CommentInfo():
    id: int
    post_id: int
    parent_id: int | None
    author: str
    text: str
    creation_date: str
    replies: list = field(default_factory=list)