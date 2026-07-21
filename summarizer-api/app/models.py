from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    title: str = Field(max_length=500)
    content: str = Field(max_length=50_000)
    category: str = Field(default="general", max_length=100)


class SummarizeResponse(BaseModel):
    title: str
    summary: str
    risk_level: str
    category: str
