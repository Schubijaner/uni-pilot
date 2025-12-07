# Uni Pilot Backend

> Backend API for Uni Pilot - A career roadmap application for university students

## 📖 Overview

Uni Pilot is a FastAPI-based backend service that provides a RESTful API for managing user profiles, generating AI-powered career roadmaps, facilitating chat interactions, and managing university modules and skills. The application uses AWS Bedrock (Claude 3) for LLM-powered features.

## ✨ Features

- **Authentication & Authorization**: JWT-based authentication system
- **User Management**: User profiles, onboarding, and preferences
- **AI-Powered Roadmaps**: Generate personalized career roadmaps using AWS Bedrock
- **Chat System**: Interactive chat with LLM for career guidance
- **Module Management**: University course/module tracking
- **Skills Tracking**: Skill assessment and progress tracking
- **Career Tree**: Career path visualization and exploration

## 🛠 Tech Stack

- **Framework**: FastAPI 0.104+
- **Language**: Python 3.11+
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **ORM**: SQLAlchemy 2.0+
- **Authentication**: JWT (python-jose)
- **LLM**: AWS Bedrock (Claude 3 Haiku/Sonnet)
- **Server**: Uvicorn
- **Testing**: Pytest with async support

## 📋 Prerequisites

- Python 3.11 or higher
- pip or conda
- AWS Account with Bedrock access (for LLM features)
- (Optional) PostgreSQL for production

## 🚀 Installation

### Using pip

1. **Clone the repository** (if not already done):
   ```bash
   cd backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Using conda

1. **Create environment from file**:
   ```bash
   conda env create -f environment.yml
   conda activate uni_pilot
   ```

2. **Install remaining dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

The application uses environment variables for configuration. Create a `.env` file in the `backend` directory:

```env
# Database
DATABASE_URL=sqlite:///uni_pilot.db

# AWS Bedrock Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
BEDROCK_MODEL_CHAT=anthropic.claude-3-haiku-20240307-v1:0
BEDROCK_MODEL_ROADMAP=anthropic.claude-3-sonnet-20240229-v1:0

# JWT Configuration
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS Configuration (comma-separated list)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# LLM Settings
MAX_CHAT_HISTORY_MESSAGES=20
CHAT_TEMPERATURE=0.7
ROADMAP_TEMPERATURE=0.1

# Logging
LOG_LEVEL=INFO
```

### Default Configuration

If no `.env` file is provided, the application uses these defaults:
- Database: SQLite (`uni_pilot.db`)
- CORS: Allows all origins (`*`)
- Secret Key: `your-secret-key-change-in-production` (⚠️ **Change in production!**)

## 🗄️ Database Setup

### Initialize Database

Run the initialization script to create tables and seed with test data:

```bash
python scripts/init_db.py
```

To drop and recreate the database:

```bash
python scripts/init_db.py --drop
```

### Test User Credentials

After initialization, you can use these test accounts:
- **Email**: `max.mustermann@stud.tu-darmstadt.de`
- **Password**: `password123`

- **Email**: `anna.schmidt@stud.tu-darmstadt.de`
- **Password**: `password123`

## 🏃 Running the Server

### Development Mode (with auto-reload)

```bash
./start_server.sh
```

Or manually:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📚 API Documentation

### Available Endpoints

- **Health**: `/health` - Health check endpoint
- **Auth**: `/api/auth/*` - Authentication endpoints (login, register)
- **Users**: `/api/users/*` - User management
- **Onboarding**: `/api/onboarding/*` - User onboarding flow
- **Modules**: `/api/modules/*` - University modules/courses
- **Roadmaps**: `/api/roadmaps/*` - Career roadmap generation and management
- **Chat**: `/api/chat/*` - AI chat interactions
- **Skills**: `/api/skills/*` - Skills management

### Interactive API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=. --cov-report=html
```

### Run Specific Test Files

```bash
pytest tests/test_api/test_auth.py
pytest tests/test_services/
```

### HTTP Test Files

The project includes HTTP test files in `tests/http/` for manual API testing. You can use these with REST clients like VS Code REST Client or IntelliJ HTTP Client.

## 📁 Project Structure

```
backend/
├── api/                    # API application code
│   ├── core/              # Core configuration and utilities
│   │   ├── config.py     # Application settings
│   │   ├── exceptions.py # Custom exceptions
│   │   └── security.py   # Security utilities (JWT, password hashing)
│   ├── models/            # Pydantic models (request/response schemas)
│   ├── routers/           # API route handlers
│   │   ├── auth.py       # Authentication routes
│   │   ├── users.py      # User management routes
│   │   ├── onboarding.py # Onboarding routes
│   │   ├── modules.py    # Module management routes
│   │   ├── roadmaps.py   # Roadmap routes
│   │   ├── chat.py       # Chat routes
│   │   └── skills.py     # Skills routes
│   ├── services/          # Business logic layer
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── roadmap_service.py
│   │   ├── chat_service.py
│   │   └── llm_service.py
│   └── prompts/           # LLM prompts
├── database/              # Database configuration
│   ├── base.py           # SQLAlchemy setup
│   └── models.py         # SQLAlchemy ORM models
├── scripts/               # Utility scripts
│   ├── init_db.py        # Database initialization
│   ├── seed_database.py  # Database seeding
│   └── ...               # Other utility scripts
├── tests/                 # Test suite
│   ├── test_api/         # API endpoint tests
│   ├── test_services/    # Service layer tests
│   └── test_database/    # Database tests
├── documentation/        # Project documentation
├── main.py               # FastAPI application entry point
├── requirements.txt      # Python dependencies
├── environment.yml       # Conda environment file
└── pytest.ini            # Pytest configuration
```

## 🔧 Available Scripts

The `scripts/` directory contains various utility scripts:

- `init_db.py` - Initialize database with tables and seed data
- `seed_database.py` - Seed database with test data
- `import_tu_darmstadt_modules.py` - Import TU Darmstadt modules
- `generate_roadmaps_for_topic_fields.py` - Generate roadmaps
- `test_skill_api.py` - Test skills API
- And more... (see `scripts/README.md` for details)

## 🔐 Security Notes

- ⚠️ **Never commit `.env` files** with real credentials
- ⚠️ **Change `SECRET_KEY`** in production
- ⚠️ **Restrict `CORS_ORIGINS`** in production to specific domains
- Use strong passwords and secure AWS credentials
- Enable HTTPS in production

## 🐛 Error Handling

The application uses custom exception classes for consistent error handling:

- `UniPilotException` - Base exception
- `NotFoundError` - 404 errors
- `ValidationError` - 400 errors
- `AuthenticationError` - 401 errors
- `LLMError` - LLM-related errors

All errors return JSON responses with `detail` and `error_code` fields.

## 📝 Logging

Logging is configured via the `LOG_LEVEL` environment variable. Available levels:
- `DEBUG`
- `INFO` (default)
- `WARNING`
- `ERROR`
- `CRITICAL`

Logs are output to stdout in the format:
```
YYYY-MM-DD HH:MM:SS - logger_name - LEVEL - message
```

## 🤝 Contributing

### Development Workflow

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Ensure all tests pass: `pytest`
5. Update documentation if needed
6. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints where possible
- Document functions and classes with docstrings
- Keep functions focused and small

## 📖 Additional Documentation

See the `documentation/` directory for detailed documentation:
- `architecture.md` - System architecture overview
- `api_endpoints.md` - API endpoint documentation
- `database_schema.md` - Database schema details
- And more...

## 👥 Team

**Backend Developers:**
- 👨‍💻 **Lukas** – Back-End Developer
- 👨‍💻 **Alexey** – Back-End Developer

## 📄 License

[Add license information here]

## 🆘 Troubleshooting

### Database Issues

If you encounter database errors:
1. Check that `uni_pilot.db` exists or run `init_db.py`
2. Verify database permissions
3. Check `DATABASE_URL` in `.env`

### AWS Bedrock Issues

If LLM features don't work:
1. Verify AWS credentials are set correctly
2. Check AWS region configuration
3. Ensure Bedrock access is enabled in your AWS account
4. Verify model IDs are correct

### Port Already in Use

If port 8000 is already in use:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process or use a different port
uvicorn main:app --port 8001
```

## 🔗 Related Links

- [Frontend Repository](../frontend/README.md)
- [Main Project README](../README.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

