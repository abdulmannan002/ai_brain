# AI Brain Vault Backend

A modular FastAPI backend for the AI Brain Vault SaaS platform, providing secure idea management and AI-powered transformations.

## Architecture

The backend follows a clean, modular architecture with clear separation of concerns:

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── core/                   # Core application components
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration management
│   │   ├── database.py        # Database connection management
│   │   └── security.py        # Authentication and security
│   ├── models/                # Pydantic data models
│   │   ├── __init__.py
│   │   ├── idea.py           # Idea-related models
│   │   ├── user.py           # User-related models
│   │   └── transform.py      # Transformation models
│   ├── services/             # Business logic services
│   │   ├── __init__.py
│   │   ├── idea_service.py   # Idea management logic
│   │   ├── user_service.py   # User management logic
│   │   ├── nlp_service.py    # NLP processing logic
│   │   ├── transform_service.py # AI transformation logic
│   │   └── voice_service.py  # Voice processing logic
│   └── api/                  # API route handlers
│       ├── __init__.py
│       ├── ideas.py          # Idea endpoints
│       ├── users.py          # User endpoints
│       ├── transform.py      # Transformation endpoints
│       └── voice.py          # Voice processing endpoints
├── tests/                    # Test suite
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container configuration
└── ai_brain_vault_service.py # Main service entry point
```

## Features

### Core Services

1. **Idea Management Service**
   - Capture ideas from text and voice input
   - Store ideas with metadata (project, theme, emotion)
   - Search and filter ideas
   - Full-text search capabilities

2. **NLP Service**
   - Automatic idea categorization using spaCy
   - Emotion detection and sentiment analysis
   - Keyword extraction and entity recognition
   - Project and theme classification

3. **Transform Service**
   - AI-powered idea transformations using LLaMA 3
   - Generate content, IP documentation, and actionable tasks
   - Fallback to OpenAI API when needed
   - Template-based generation for development

4. **Voice Service**
   - Audio transcription using OpenAI Whisper
   - S3 storage for audio files
   - Audio format validation
   - Idea extraction from voice input

5. **User Management Service**
   - Auth0 integration for authentication
   - User profile management
   - Subscription tier handling
   - User statistics and analytics

### API Endpoints

#### Ideas API (`/api/v1/ideas`)
- `POST /` - Create a new idea
- `GET /` - Get user's ideas with filtering
- `GET /{idea_id}` - Get specific idea
- `PUT /{idea_id}` - Update an idea
- `DELETE /{idea_id}` - Delete an idea
- `GET /stats/summary` - Get user statistics

#### Users API (`/api/v1/users`)
- `GET /me` - Get current user profile
- `PUT /me` - Update user profile
- `DELETE /me` - Delete user account

#### Transform API (`/api/v1/transform`)
- `POST /` - Transform idea using AI

#### Voice API (`/api/v1/voice`)
- `POST /transcribe` - Transcribe audio file
- `POST /extract-ideas` - Extract ideas from audio

## Technology Stack

- **Framework**: FastAPI with async/await support
- **Database**: PostgreSQL with asyncpg
- **Authentication**: Auth0 with JWT tokens
- **AI/ML**: 
  - LLaMA 3 via x.AI API
  - OpenAI Whisper for speech-to-text
  - spaCy for NLP processing
- **Cloud Services**: AWS S3 for file storage
- **Message Queue**: Apache Kafka for async processing
- **Testing**: pytest with async support

## Configuration

The application uses Pydantic Settings for configuration management. Key configuration areas:

### Environment Variables

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_brain_vault
DB_USER=postgres
DB_PASSWORD=postgres

# AWS
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET=ai-brain-vault-audio

# AI APIs
XAI_API_KEY=your_xai_key
OPENAI_API_KEY=your_openai_key

# Auth0
AUTH0_DOMAIN=your_domain.auth0.com
AUTH0_AUDIENCE=your_audience
AUTH0_ISSUER=https://your_domain.auth0.com/

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Application
DEBUG=false
CORS_ORIGINS=["http://localhost:3000"]
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install spaCy model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Run database migrations**
   ```bash
   # Ensure PostgreSQL is running and database exists
   psql -U postgres -d ai_brain_vault -f ../database/schema.sql
   ```

7. **Start the application**
   ```bash
   python ai_brain_vault_service.py
   ```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_api.py
```

### Code Quality

```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Docker Deployment

```bash
# Build image
docker build -t ai-brain-vault-backend .

# Run container
docker run -p 8000:8000 --env-file .env ai-brain-vault-backend
```

## Kubernetes Deployment

The backend is configured for Kubernetes deployment with:
- Horizontal Pod Autoscaler
- Health checks and readiness probes
- Resource limits and requests
- ConfigMap and Secret management

See the `k8s/` directory for deployment manifests.

## Monitoring

The application includes:
- Health check endpoints
- Structured logging
- Metrics collection (Prometheus compatible)
- Error tracking and alerting

## Security

- JWT token validation
- CORS configuration
- Input validation with Pydantic
- SQL injection prevention with parameterized queries
- File upload validation
- Rate limiting (configurable)

## Contributing

1. Follow the modular architecture pattern
2. Add tests for new features
3. Update documentation
4. Use type hints throughout
5. Follow PEP 8 style guidelines

## License

This project is licensed under the MIT License. 