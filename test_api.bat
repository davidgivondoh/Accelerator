@echo off
echo Testing Growth Engine Phase 1 Implementation
echo ===========================================
echo.

echo 1. Testing Health Endpoint...
curl -X GET "http://localhost:8000/api/v1/health" -H "accept: application/json"
echo.
echo.

echo 2. Testing Search Endpoint...
curl -X GET "http://localhost:8000/api/v1/search?q=software&limit=5" -H "accept: application/json"
echo.
echo.

echo 3. Testing Cache Stats...
curl -X GET "http://localhost:8000/api/v1/cache/stats" -H "accept: application/json"
echo.
echo.

echo 4. Testing Filter Categories...
curl -X GET "http://localhost:8000/api/v1/filters/categories" -H "accept: application/json"
echo.
echo.

echo Phase 1 API Testing Complete!
pause