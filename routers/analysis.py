# analysis.py router file for ai agent

from fastapi import APIRouter, status, HTTPException
from database import SessionDep
from schemas.analysis import AnalysisRequest, AnalysisResponse, SentimentBreakdown
from models.analysis import AnalysisRecord
from services.news_client import NewsClient, NewsAPIError
from services.ai_agent import analyze_articles
from sqlalchemy import select, desc

# Service function to turn record into response
def _record_to_response(record:AnalysisRecord) ->AnalysisResponse:
    return AnalysisResponse(id=record.id,
                            topic=record.topic,
                            days=record.days,
                            articles_found=record.articles_found,
                            articles_analyzed=record.articles_analyzed,
                            sentiment=SentimentBreakdown(
                                positive=record.sentiment_positive,
                                neutral=record.sentiment_neutral,
                                negative=record.sentiment_negative),
                            summary=record.summary,
                            key_events=record.key_events,
                            sources=record.sources,
                            ai_provider_used=record.ai_provider_used,
                            created_at=record.created_at)


# Router for analysis
analysis_router = APIRouter(prefix="/analysis",
                            tags=["analysis"])
# ANALYSIS ENDPOINTS
# POST analysis, gets AlalysisRequest, returns
# AnalysisResponse
@analysis_router.post("/",
                      status_code=status.HTTP_201_CREATED,
                      description="Create news analysis regarding input data")
async def analysis_make(session:SessionDep,
    request:AnalysisRequest) -> AnalysisResponse:
# Calling news client fetch articles service function
    news_client= NewsClient()
    try:
        articles = await news_client.fetch_articles(topic=request.topic, 
                                                    days=request.days, 
                                                    language=request.language,
                                                    max_articles=10)

# News API error exception
    except NewsAPIError:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                            detail="News API error")
    else:

# Empty articles exception
        if not articles:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No articles found")

# Calling analyze articles service function
        try:
            result_dict, provider_name = await analyze_articles(topic=request.topic, 
                                                                articles=articles)
# Runtime error exception                                                                
        except RuntimeError:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail="Runtime error")
        else:

# Creating analysis_record to add to db
            analysis_record = AnalysisRecord()
            analysis_record.topic = request.topic
            analysis_record.days = request.days
            analysis_record.articles_found = len(articles)
            analysis_record.articles_analyzed = len(result_dict["relevant_articles"])
            analysis_record.sentiment_positive = len([res_el for res_el in result_dict["relevant_articles"] if res_el["sentiment"]=="positive"])
            analysis_record.sentiment_neutral = len([res_el for res_el in result_dict["relevant_articles"] if res_el["sentiment"]=="neutral"])
            analysis_record.sentiment_negative = len([res_el for res_el in result_dict["relevant_articles"] if res_el["sentiment"]=="negative"])
            analysis_record.summary = result_dict["summary"]
            analysis_record.key_events = result_dict["key_events"]
            analysis_record.sources = result_dict.get("relevant_articles",[])
            analysis_record.ai_provider_used = provider_name

# adding analysis_record to db
            session.add(analysis_record)
            await session.commit()
            await session.refresh(analysis_record)

# Creating result
            return _record_to_response(analysis_record)
        
# GET analysis, return list of resent analysis
@analysis_router.get("/",
                     status_code=status.HTTP_200_OK,
                     description="Get list of recent analysis")
async def analysis_get_list(session:SessionDep,
                            limit:int=20,
                            offset:int=0) ->list[AnalysisResponse]:
# Selecting analysis from db via request values
    query = select(AnalysisRecord).order_by(desc(AnalysisRecord.created_at)).offset(offset).limit(limit)
    result = await session.execute(query)
    analysis_list = result.scalars().all()

# Creating output
    output_list=[]
    for analysis in analysis_list:
        output_list.append(_record_to_response(analysis))
    return output_list        

# GET analysis via its id in database
@analysis_router.get("/{analysis_id}",
                     status_code=status.HTTP_200_OK,
                     description="Select analysis via its id")
async def analysis_get(analysis_id:int,
                       session:SessionDep) -> AnalysisResponse:
# Looking for analysis with such id
    analysis_found = await session.get(AnalysisRecord, analysis_id)

# exception if none found
    if not analysis_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Analysis with id {analysis_id} not found")
# Creating result
    return _record_to_response(analysis_found)