# test_analysis.py, includes tests for app

'''
Tests for AI News Analyst endpoints:
- create (POST /Analysis/)
- retrieve list (GET /Analysis/)
- retrieve by id (GET /analysis/{analysis_id})
'''

import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

#MOCKS
MOCK_ARTICLES = [
    {
        "title": "1st car article",
        "description":"Cars:history",
        "url":"https://fake_url1.org",
        "published_at":"2024-07-01T10:00:00Z",
        "source":"Fake cars magazine"
    },
    {
        "title": "2nd car article",
        "description":"Cars:technology",
        "url":"https://fake_url2.org",
        "published_at":"2024-08-01T10:00:00Z",
        "source":"Fake cars magazine"
    },
    {
        "title": "3d car article",
        "description":"Cars:prices",
        "url":"https://fake_url3.org",
        "published_at":"2024-09-01T10:00:00Z",
        "source":"Fake cars magazine"
    }
]
MOCK_RESULT ={
    "relevant_articles": 
    [
        {
            "title": "1st car article",
            "url":"https://fake_url1.org",
            "published_at":"2024-07-01T10:00:00Z",
            "source":"Fake cars magazine",
            "sentiment":"positive"
        },
        {
            "title": "2nd car article",
            "url":"https://fake_url2.org",
            "published_at":"2024-07-11T10:00:00Z",
            "source":"Fake cars magazine",
            "sentiment":"neutral"
        },
        {
            "title": "3d car article",
            "url":"https://fake_url3.org",
            "published_at":"2024-07-21T10:00:00Z",
            "source":"Fake cars magazine",
            "sentiment":"negative"
        }
  ],
  "summary": "Articles cover cars history, technology and prices",
  "key_events": ["car history", "car technonly", "car prices", "cars"]
}

# TESTS WITHOUT MOCKS
# Health test, GET "/"
async def test_health(client:AsyncClient):
# Making GET request
    response = await client.get("/")

# Result check
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "You`re on AI News Analyst frontpage"

# Topic short length check, POST 
async def test_validation_topic_too_short(client:AsyncClient):
# Making POST request
    response = await client.post("/analysis/", json={
        "topic":"x",
        "days":1,
        "language":"en"
    })

# Result check
    assert response.status_code == 422

# ID not found check, GET
async def test_get_by_id_not_found(client:AsyncClient):
# Making GET request
    response = await client.get("/analysis/99999")

# Result check
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Analysis with id 99999 not found"

# MOCK TESTS
# Success analysis creation check, POST
async def test_create_analysis(client:AsyncClient):
    with patch("routers.analysis.NewsClient") as MockClient:

# fetch_articles setup
        MockClient.return_value.fetch_articles=AsyncMock(return_value=MOCK_ARTICLES)
        with patch("routers.analysis.analyze_articles", new_callable=AsyncMock) as mock_analyze:
            mock_analyze.return_value = (MOCK_RESULT, "groq")

# Making POST request
            response = await client.post("/analysis/", json={
                "topic":"cars",
                "days":30,
                "language":"en"
            })

# Result check 
    assert response.status_code == 201
    data=response.json()
    assert data["topic"] == "cars"
    assert data["articles_found"] == 3
    assert data["sentiment"]["positive"] == 1
    assert data["sentiment"]["neutral"] == 1
    assert data["sentiment"]["negative"] == 1
    assert data["ai_provider_used"] == "groq"
    assert data["summary"] == "Articles cover cars history, technology and prices"
    assert data["key_events"] == ["car history", "car technonly", "car prices", "cars"]

# No articles for analysis found check, POST
async def test_no_articles_found(client:AsyncClient):
    with patch("routers.analysis.NewsClient") as MockClient:

# fetch_articles setup
        MockClient.return_value.fetch_articles=AsyncMock(return_value=[]) 

# Making POST request
        response = await client.post("/analysis/", json={
            "topic":"Tesla",
            "days":30,
            "language":"en"
        })

# Result check
    assert response.status_code == 404
    data=response.json()
    assert data["detail"] == "No articles found"

# get analysis list check, GET
async def test_get_history(client:AsyncClient):
    with patch("routers.analysis.NewsClient") as MockClient:

# fetch_articles setup, making post
        MockClient.return_value.fetch_articles=AsyncMock(return_value=MOCK_ARTICLES)
        with patch("routers.analysis.analyze_articles", new_callable=AsyncMock) as mock_analyze:
            mock_analyze.return_value = (MOCK_RESULT, "groq")

 # Making POST request
            await client.post("/analysis/", json={
                "topic":"cars",
                "days":30,
                "language":"en"
            })

# Making GET request
    response = await client.get("/analysis/")

# Result check
    assert response.status_code == 200
    data_list = response.json()
    assert len(data_list) > 0

# Analysis selection via ID check, GET 
async def test_get_by_id(client:AsyncClient):
    with patch("routers.analysis.NewsClient") as MockClient:

# fetch_articles setup, making post
        MockClient.return_value.fetch_articles=AsyncMock(return_value=MOCK_ARTICLES)
        with patch("routers.analysis.analyze_articles", new_callable=AsyncMock) as mock_analyze:
            mock_analyze.return_value = (MOCK_RESULT, "groq")

        # Making POST request
            response = await client.post("/analysis/", json={
                "topic":"cars",
                "days":30,
                "language":"en"
            })
            id_check = response.json()["id"]

# Making GET request
    response = await client.get(f"/analysis/{id_check}")
 
 # Result check
    assert response.status_code == 200
    data=response.json()
    assert data["topic"] == "cars"
    assert data["articles_found"] == 3
    assert data["sentiment"]["positive"] == 1
    assert data["sentiment"]["neutral"] == 1
    assert data["sentiment"]["negative"] == 1
    assert data["ai_provider_used"] == "groq"
    assert data["summary"] == "Articles cover cars history, technology and prices"
    assert data["key_events"] == ["car history", "car technonly", "car prices", "cars"]