@echo off
REM Quick deployment script for Windows

echo 🚀 Karma System Quick Deploy
echo ============================

REM Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)

REM Check if .env exists
if not exist .env (
    echo ❌ .env file not found! Please create it first.
    pause
    exit /b 1
)

echo ✅ Stopping existing services...
docker-compose down

echo ✅ Starting services...
docker-compose up -d --build

echo ✅ Waiting for services to start...
timeout /t 15 /nobreak >nul

echo ✅ Running database migrations...
docker-compose exec -T api alembic upgrade head

echo ✅ Running tests...
python scripts\test_bot.py

echo 🎉 Deployment completed!
echo.
echo 📋 Service URLs:
echo - API Docs: http://localhost:8000/docs
echo - Grafana: http://localhost:3000 (admin/admin)
echo - Bot logs: docker-compose logs -f bot
echo.
pause
