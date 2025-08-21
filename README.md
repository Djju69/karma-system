# Karma System - Telegram Bot & API

A comprehensive Telegram bot and API system for partner management with QR code rewards, multi-language support, and geolocation features.

## 🚀 Features

### Bot Features
- **Multi-language support** (Russian, English, Vietnamese, Korean)
- **Partner registration** with FSM flow
- **QR code generation** with Fernet encryption
- **Geolocation coverage** checking with PostGIS
- **City-based catalog** browsing with pagination
- **Role-based access control** (User, Partner, Admin)
- **Redis caching** for performance optimization

### API Features
- **Partner management** endpoints
- **QR code validation** and redemption
- **Listing management** with filters
- **RESTful architecture** with FastAPI
- **Async database operations** with SQLAlchemy 2

### Technical Stack
- **Python 3.11+**
- **aiogram v3** for Telegram bot
- **FastAPI** for REST API
- **PostgreSQL 15** with PostGIS extension
- **Redis 7** for caching and FSM storage
- **SQLAlchemy 2** async ORM
- **Alembic** for database migrations
- **Docker & docker-compose** for containerization

## 📁 Project Structure

```
app/
├── api/                    # FastAPI application
│   ├── routes/            # API endpoints
│   └── main.py           # FastAPI app entry point
├── bot/                   # Telegram bot
│   ├── routers/          # Bot command handlers
│   ├── keyboards/        # Reply and inline keyboards
│   ├── middlewares/      # Bot middlewares
│   ├── fsm/             # Finite State Machine states
│   ├── i18n/            # Internationalization files
│   └── main.py          # Bot entry point
├── core/                  # Core business logic
│   ├── services/        # Business services
│   ├── cache.py         # Redis cache service
│   ├── authz.py         # Authorization service
│   └── geo.py           # Geolocation service
├── db/                    # Database layer
│   ├── models.py        # SQLAlchemy models
│   └── database.py      # Database configuration
└── infra/                 # Infrastructure configs
    ├── nginx/           # Nginx configuration
    ├── prometheus/      # Monitoring configuration
    └── grafana/         # Dashboard configuration
```

## 🛠️ Installation & Setup

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)

### Environment Variables

Create `.env` file with the following variables:

```bash
# Bot Configuration
BOT_TOKEN=your_telegram_bot_token
FERNET_KEY_HEX=64_character_hex_string_for_encryption
DEFAULT_LANG=ru
DEFAULT_CITY_SLUG=nhatrang

# Database
DATABASE_URL=postgresql+asyncpg://karma_user:karma_password@postgres:5432/karma_db

# Redis
REDIS_URL=redis://redis:6379/0

# Security
PHONE_SALT=your_phone_hash_salt

# Policy PDFs (per language)
USER_POLICY_PDF_RU=https://example.com/user_policy_ru.pdf
USER_POLICY_PDF_EN=https://example.com/user_policy_en.pdf
USER_POLICY_PDF_VI=https://example.com/user_policy_vi.pdf
USER_POLICY_PDF_KO=https://example.com/user_policy_ko.pdf

PARTNER_POLICY_PDF_RU=https://example.com/partner_policy_ru.pdf
PARTNER_POLICY_PDF_EN=https://example.com/partner_policy_en.pdf
PARTNER_POLICY_PDF_VI=https://example.com/partner_policy_vi.pdf
PARTNER_POLICY_PDF_KO=https://example.com/partner_policy_ko.pdf

# Support
SUPPORT_TELEGRAM=@your_support_username
WEBAPP_QR_URL=https://your-domain.com/qr-scanner
```

### Quick Start with Docker

1. **Clone and setup**:
```bash
git clone <repository>
cd TESTKARMA
cp .env.example .env  # Edit with your values
```

2. **Start services**:
```bash
docker-compose up -d
```

3. **Run database migrations**:
```bash
docker-compose exec api alembic upgrade head
```

4. **Check services**:
- Bot: Check Telegram bot is responding
- API: http://localhost:8000/docs
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090

### Local Development

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Setup database**:
```bash
# Start PostgreSQL and Redis
docker-compose up postgres redis -d

# Run migrations
alembic upgrade head
```

3. **Run services**:
```bash
# Bot
python -m app.bot.main

# API (in another terminal)
uvicorn app.api.main:app --reload
```

## 🗄️ Database Schema

### Core Tables
- **cities** - Operating cities with PostGIS coverage areas
- **users** - Telegram users with roles and preferences
- **partner_profiles** - Partner business information
- **listings** - Business listings with geolocation
- **qr_issues** - QR code issuance and redemption tracking
- **partner_applications** - Partner registration requests

### Key Features
- **PostGIS integration** for geolocation queries
- **JSONB fields** for flexible settings storage
- **Proper indexing** for performance
- **Foreign key constraints** for data integrity

## 🔧 API Endpoints

### Partners
- `POST /partners/applications` - Create partner application
- `POST /partners/web-auth` - Create web authentication
- `POST /partners/applications/{id}/approve` - Approve application
- `GET /partners/listings/{user_id}` - Get partner listings

### QR Codes
- `POST /qr/redeem` - Redeem QR code
- `GET /qr/validate/{jti}` - Validate QR code
- `GET /qr/image/{jti}` - Get QR code image

### Listings
- `GET /listings/` - Get paginated listings with filters
- `GET /listings/{id}` - Get single listing

## 🤖 Bot Commands

### User Commands
- `/start` - Initialize bot, language selection
- **🗂 Категории** - Browse business categories
- **👤 Личный кабинет** - User profile management
- **📍 Районы/Рядом** - Location-based search
- **❓ Помощь** - Help and support

### Partner Features
- Partner registration FSM flow
- QR code generation for offers
- Business listing management
- Web authentication setup

## 🌐 Internationalization

Supported languages:
- **Russian (ru)** - Default
- **English (en)**
- **Vietnamese (vi)**
- **Korean (ko)**

Translation files located in `app/bot/i18n/` with complete coverage of all UI elements.

## 🔒 Security Features

- **Fernet encryption** for QR code payloads
- **Phone number hashing** with salt
- **Role-based access control**
- **Rate limiting** via Nginx
- **Atomic QR redemption** to prevent race conditions

## 📊 Monitoring

- **Prometheus** metrics collection
- **Grafana** dashboards for visualization
- **Health checks** for all services
- **Structured logging** with no PII exposure

## 🚀 Deployment

### Railway Deployment
1. Connect repository to Railway
2. Set environment variables
3. Deploy with automatic builds

### Manual Deployment
1. Build and push Docker images
2. Setup PostgreSQL with PostGIS
3. Configure Nginx with SSL
4. Run database migrations
5. Start services with docker-compose

## 📝 Development Notes

### Key Design Decisions
- **Immutable callback patterns** for bot stability
- **Redis FSM storage** with memory fallback
- **Async-first architecture** for performance
- **Service layer pattern** for business logic
- **Comprehensive error handling** with user-friendly messages

### Testing
- Unit tests for services and utilities
- Integration tests for API endpoints
- FSM flow testing for bot interactions
- QR code race condition testing

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Follow code style guidelines
4. Add tests for new features
5. Submit pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For technical support, contact: ${SUPPORT_TELEGRAM}

---

**Built with ❤️ for the Karma System community**
