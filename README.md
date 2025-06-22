# AI Brain Vault

A SaaS platform designed to solve the problem of losing valuable ideas by providing a "second brain" system for creative professionals, entrepreneurs, and teams.

## 🎯 Problem Statement

2025 Challenge: Smart individuals and teams generate too many ideas but lose ~90% due to scattered notes, unposted content, or unbuilt projects.

**Solution**: A $20K-valued system that captures every idea, organizes them intelligently, and uses AI to generate value (e.g., blog posts, patent outlines, tasks).

## ✨ Key Features

### 🎯 Idea Capture
- **Text Input**: Web/mobile forms for manual idea entry
- **Voice Input**: Speech-to-text using OpenAI Whisper
- **Tweet Capture**: Twitter/X API integration (planned)
- **Email Integration**: Automatic idea extraction (planned)

### 🧠 AI-Powered Organization
- **Project Clustering**: Automatic categorization by project type
- **Theme Extraction**: NLP-based topic identification
- **Emotion Analysis**: Sentiment classification using LLaMA 3
- **Smart Search**: Full-text search with filters

### ⚡ Idea Transformation
- **Blog Posts**: Generate engaging content from ideas
- **IP Summaries**: Create patent-like concept outlines
- **Actionable Tasks**: Convert ideas into prioritized to-dos

### 👥 Team Collaboration
- **Shared Projects**: Collaborate on idea collections
- **User Management**: Role-based access control
- **Real-time Updates**: Live idea sharing and feedback

## 🏗️ Architecture

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | Next.js 14 (TypeScript) | Modern web app with SSR |
| **Backend** | FastAPI (Python) | High-performance async APIs |
| **Database** | PostgreSQL (AWS RDS) | Reliable data storage |
| **File Storage** | AWS S3 | Audio files and generated content |
| **Message Queue** | Apache Kafka (AWS MSK) | Async processing |
| **AI/ML** | LLaMA 3 (xAI API) + spaCy | NLP and content generation |
| **Authentication** | Auth0 | Secure user management |
| **Speech-to-Text** | OpenAI Whisper | Voice input processing |
| **Deployment** | Kubernetes (AWS EKS) | Scalable container orchestration |
| **Monitoring** | Prometheus + Grafana | Observability and alerting |

### Microservices Architecture

```
[Users] → [Next.js Frontend] → [API Gateway] → [FastAPI Services]
                                    ↓
[PostgreSQL] ← [Capture Service] ← [NLP Service] ← [Transform Service]
                                    ↓
[Kafka] → [S3] → [Monitoring Stack]
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+
- Kubernetes cluster (for production)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/ai-brain-vault.git
   cd ai-brain-vault
   ```

2. **Set up environment variables**
   ```bash
   # Backend (.env)
   cp backend/.env.example backend/.env
   # Edit with your actual values
   
   # Frontend (.env.local)
   cp frontend/.env.example frontend/.env.local
   # Edit with your actual values
   ```

3. **Start the database**
   ```bash
   docker-compose up postgres -d
   ```

4. **Run database migrations**
   ```bash
   psql -h localhost -U postgres -d ai_brain_vault -f database/schema.sql
   ```

5. **Start the backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn ai_brain_vault_service:app --reload
   ```

6. **Start the frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

7. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Production Deployment

1. **Build Docker images**
   ```bash
   docker build -t ai-brain-backend:latest backend/
   docker build -t ai-brain-frontend:latest frontend/
   ```

2. **Deploy to Kubernetes**
   ```bash
   kubectl apply -f k8s/namespace.yaml
   kubectl apply -f k8s/postgres-secret.yaml
   kubectl apply -f k8s/postgres-deployment.yaml
   kubectl apply -f k8s/backend-deployment.yaml
   kubectl apply -f k8s/frontend-deployment.yaml
   kubectl apply -f k8s/ingress.yaml
   kubectl apply -f k8s/monitoring/
   ```

3. **Set up monitoring**
   ```bash
   kubectl port-forward svc/grafana 3000:3000 -n ai-brain-vault
   kubectl port-forward svc/prometheus 9090:9090 -n ai-brain-vault
   ```

## 📊 API Documentation

### Authentication

All API endpoints require authentication via Auth0 JWT tokens.

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/ideas/
```

### Core Endpoints

#### Ideas Management

```bash
# Create a new idea
POST /ideas/
{
  "content": "Your idea here",
  "source": "manual"
}

# Get user's ideas
GET /ideas/?project=Startup&theme=tech&emotion=excited

# Search ideas
GET /ideas/search/?q=artificial intelligence

# Voice input
POST /ideas/voice/
# Multipart form with audio file
```

#### Transformations

```bash
# Transform idea to content
POST /transform/
{
  "idea_id": 123,
  "output_type": "content",
  "user_id": "user_123"
}
```

#### User Management

```bash
# Get current user info
GET /users/me

# Create new user
POST /users/
{
  "auth0_id": "auth0|123",
  "email": "user@example.com",
  "subscription": "premium"
}
```

## 💰 Monetization Model

### Free Tier
- 50 ideas per month
- Basic sorting and organization
- Text input only
- Community support

### Premium ($15/month)
- Unlimited ideas
- Voice input processing
- Team collaboration
- Advanced AI features
- Priority support

### Enterprise ($100+/month)
- Everything in Premium
- Custom integrations
- API access
- Dedicated support
- SLA guarantees

## 🔧 Configuration

### Environment Variables

#### Backend
```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_brain_vault
DB_USER=postgres
DB_PASSWORD=your_password

# AWS
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
S3_BUCKET=ai-brain-vault-audio

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# xAI API
XAI_API_KEY=your_xai_key

# Auth0
AUTH0_DOMAIN=your_domain.auth0.com
AUTH0_AUDIENCE=your_audience
```

#### Frontend
```bash
# Backend API
BACKEND_URL=http://localhost:8000

# Auth0
AUTH0_SECRET=your_secret
AUTH0_ISSUER_BASE_URL=https://your_domain.auth0.com
AUTH0_BASE_URL=http://localhost:3000
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_client_secret
AUTH0_AUDIENCE=your_audience
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pip install pytest pytest-asyncio httpx
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

### Integration Tests
```bash
# Run full integration test suite
./scripts/test-integration.sh
```

## 📈 Monitoring & Observability

### Metrics
- API response times and error rates
- Database query performance
- Kafka message throughput
- xAI API usage and costs
- User engagement metrics

### Alerts
- High error rates (>5%)
- API latency spikes (>2s)
- Database connection issues
- xAI API quota limits
- Disk space warnings

### Dashboards
- System health overview
- User activity analytics
- Revenue and subscription metrics
- AI processing performance

## 🔒 Security

### Authentication & Authorization
- Auth0 OAuth 2.0 integration
- JWT token validation
- Role-based access control
- Session management

### Data Protection
- Encrypted data at rest
- TLS for data in transit
- Regular security audits
- GDPR compliance

### API Security
- Rate limiting
- Input validation
- SQL injection prevention
- CORS configuration

## 🚀 Roadmap

### Phase 1 (MVP) - Completed ✅
- [x] Basic idea capture and storage
- [x] NLP-powered organization
- [x] AI transformation features
- [x] User authentication
- [x] Web interface

### Phase 2 (Beta) - In Progress 🔄
- [ ] Twitter/X API integration
- [ ] Mobile PWA
- [ ] Team collaboration features
- [ ] Advanced analytics
- [ ] Performance optimization

### Phase 3 (Production) - Planned 📋
- [ ] Enterprise features
- [ ] Custom integrations
- [ ] Advanced AI models
- [ ] Global deployment
- [ ] Marketplace ecosystem

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow the existing code style
- Add tests for new features
- Update documentation
- Ensure all tests pass
- Follow semantic versioning

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.ai-brain-vault.com](https://docs.ai-brain-vault.com)
- **Issues**: [GitHub Issues](https://github.com/your-username/ai-brain-vault/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/ai-brain-vault/discussions)
- **Email**: support@ai-brain-vault.com

## 🙏 Acknowledgments

- OpenAI for Whisper speech-to-text
- xAI for LLaMA 3 API access
- Auth0 for authentication services
- The open-source community for amazing tools and libraries

---

**AI Brain Vault** - Never lose another great idea! 💡 