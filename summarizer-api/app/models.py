from pydantic import BaseModel


class SummarizeRequest(BaseModel):
    title: str
    content: str
    category: str = "general"


class SummarizeResponse(BaseModel):
    title: str
    summary: str
    risk_level: str
    category: str
