# Karma System Manual Testing Guide

## 🚀 Quick Start

### 1. Deploy the bot
```bash
# Windows
scripts\quick_deploy.bat

# Linux/Mac  
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### 2. Run automated tests
```bash
python scripts/test_bot.py
```

## 📱 Manual Bot Testing

### Test 1: Basic Commands
1. Send `/start` to bot
2. Choose language (ru/en/vi/ko)
3. Accept policy
4. Verify main menu appears

**Expected:** 
- 🗂 Категории
- 👤 Личный кабинет  
- 📍 Районы/Рядом
- ❓ Помощь

### Test 2: Language Switching
1. Go to 👤 Личный кабинет
2. Select "Язык"
3. Change to English
4. Verify interface switches to English

### Test 3: Partner Registration FSM
1. Go to 👤 Личный кабинет
2. Select "Стать партнером"
3. Follow 5-step process:
   - Company name
   - Business description
   - Category selection
   - Offer details
   - Confirmation

**Check:** Application saved in database

### Test 4: Catalog Browsing
1. Select 🗂 Категории
2. Choose "Рестораны"
3. Test filters (asia, europe, street, vege)
4. Navigate pages (5 items per page)
5. View listing details

### Test 5: QR Code Generation
1. Complete partner registration
2. Access QR creation
3. Generate QR code
4. Verify image appears

## 🔧 API Testing

### Test API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Validate QR
curl http://localhost:8000/qr/validate/test-jti

# Get listings
curl "http://localhost:8000/listings/?city_id=1&category=restaurants&page=1"
```

## 🐛 Troubleshooting

### Bot not responding
```bash
# Check logs
docker-compose logs bot

# Restart bot
docker-compose restart bot
```

### Database issues
```bash
# Check connection
docker-compose exec postgres pg_isready -U karma_user -d karma_db

# Run migrations
docker-compose exec api alembic upgrade head
```

### Redis issues
```bash
# Check Redis
docker-compose exec redis redis-cli ping

# Restart Redis
docker-compose restart redis
```

## ✅ Success Criteria

- [ ] Bot responds to /start
- [ ] Language switching works
- [ ] FSM flows complete without errors
- [ ] Catalog pagination works
- [ ] QR codes generate successfully
- [ ] API endpoints return valid responses
- [ ] No errors in logs

## 📊 Performance Checks

- Response time < 2 seconds
- Memory usage stable
- No memory leaks
- Redis cache hit rate > 80%
