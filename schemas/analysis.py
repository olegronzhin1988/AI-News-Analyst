# analysis.py, includes schemas for ai agent actions

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
# Schema for POST endpoint input
class AnalysisRequest(BaseModel):
    topic:str = Field(default=...,
                      title="Analysis topic",
                      description="Topic ai agent uses to analyze news articles",
                      min_length=2,
                      max_length=100)
    days:int = Field(default=7,
                    title="Searh days",
                    description="Days back from today used to search news articles",
                    ge=1,
                    le=30)
    language:str = Field(default="en")

# Sentiment evaluation
class SentimentBreakdown(BaseModel):
    positive:int = Field(default=0,
                            title="Positive evaluation",
                            description="Number of articles evaluated positivly",
                            ge=0)
    neutral:int = Field(default=0,
                            title="Neutral evaluation",
                            description="Number of articles evaluated neutrally",
                            ge=0)
    negative:int = Field(default=0,
                            title="Negative evaluation",
                            description="Number of articles evaluated negativly",
                            ge=0)

# API response schema 
class AnalysisResponse(BaseModel):
    id:int = Field(default=...,
                   title="Analysis ID",
                   description="Analysis ID in database",
                   ge=1)
    topic:str = Field(default=...,
                      title="Analysis topic",
                      description="Topic ai agent uses to analyze news articles",
                      min_length=2,
                      max_length=100)
    days:int = Field(default=7,
                    title="Searh days",
                    description="Days back from today used to search news articles",
                    ge=1,
                    le=30) 
    articles_found:int = Field(default=0,
                               title="Articles found",
                               description="articles found on topic",
                               ge=0)
    articles_analyzed:int = Field(default=0,
                                  title="Articles analyzed",
                                   description="Amount of analyzed articles",
                                   ge=0)
    sentiment:SentimentBreakdown = Field(title="Sentiment Analysis",
                                        description="Quantifical sentiment analysis of articles on topic")
    summary:str = Field(default =...,
                        title="Analysis summary",
                        description="Summary of articles on topic")
    key_events:list[str] = Field(title="Key events",
                                 description="Key events on topic, found in articles")
    sources:list[dict] = Field(title="Sources",
                               description="Source material used in analysis")
    ai_provider_used:str = Field(title="AI Provider",
                                 description="AI provider used for analysis")
    created_at:datetime = Field(title="Created at",
                                description="Analysis` creation date and time")
    model_config = ConfigDict(from_attributes=True)