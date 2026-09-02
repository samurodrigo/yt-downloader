from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Video:
    id: str
    title: str
    url: str

    channel: Optional[str] = None
    duration: Optional[int] = None
    thumbnail: Optional[str] = None

    selected: bool = True

    formats: list = field(default_factory=list)

    selected_format: str = "mp4"
    selected_quality: str = "best"