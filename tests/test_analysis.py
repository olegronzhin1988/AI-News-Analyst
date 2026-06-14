# test_analysis.py, includes tests for app

'''
Tests for AI News Analyst endpoints:
- create (POST /Analysis/)
- retrieve list (GET /Analysis/)
- retrieve by id (GET /analysis/{analysis_id})
'''


import pytest
from httpx import AsyncClient
from typing import Dict, Any

class TestTasksCreate:
    """Tests for creating"""