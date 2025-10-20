from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel, Field


class RoutingChoice(BaseModel):
    your_choice: Literal[
        "howtoeat",
        "howtocook",
        "howtoexercise",
        "howtosleep",
        "general",
        "none",
    ] = Field(description="选择路由目标；无需转交则 general/none")
    task_description: Optional[str] = Field(default=None, description="任务补充")


