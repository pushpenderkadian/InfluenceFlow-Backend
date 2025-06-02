# 🚀 Influency - End-to-End Influencer Marketing Automation Platform

Influency is a comprehensive FastAPI-based backend platform with microservices architecture that automates the entire influencer marketing workflow from creator discovery to campaign completion and payment processing. The platform features distributed services for email automation, WhatsApp business communication, and real-time message processing.

## ✨ Key Features

### 🔍 AI-Powered Creator Discovery
- **Vector-based search** using Pinecone for semantic creator matching
- **Advanced filtering** by follower count, engagement rate, location, category
- **Multi-platform support** (Instagram, YouTube, TikTok, Twitter)

### 📧 Automated Outreach & Communication
- **Email automation** with dedicated microservice for scalable delivery
- **WhatsApp Business API integration** with dedicated service on port 8001
- **Message queue processing** with RabbitMQ for reliable delivery
- **Template-based messaging** with personalization
- **Real-time communication** status tracking

### 📋 Campaign Management
- **End-to-end campaign lifecycle** management
- **Creator invitation and acceptance** workflow
- **Real-time status tracking** and updates

### 📄 Contract & Legal Automation
- **Digital contract generation** with customizable templates
- **E-signature integration** support
- **Automated contract delivery** and tracking

### 💰 Payment Processing
- **Multi-stage payment** support (advance, milestone, final)
- **Automated payment notifications** via email
- **Invoice generation** and tracking

### 📊 Performance Analytics
- **ROI tracking** and campaign performance metrics
- **Engagement analytics** across all platforms
- **Revenue attribution** and conversion tracking

## 🏗️ Architecture

### 🌐 Microservices Architecture
Influency follows a distributed microservices architecture with the following components:

#### Main API Server (Port 8000)
- **Core FastAPI application** handling main business logic
- **Authentication & authorization** with JWT tokens
- **Campaign and creator management** endpoints
- **Database operations** with PostgreSQL

#### WhatsApp Business Service (Port 8001)
- **Dedicated WhatsApp Business API** integration
- **Independent FastAPI service** for WhatsApp operations
- **Message sending and webhook handling**
- **Business account management**

#### Email Service Consumer (Background)
- **Asynchronous email processing** using RabbitMQ
- **Template-based email generation**
- **SMTP integration** with retry mechanisms
- **Email delivery status tracking**

#### WhatsApp Service Consumer (Background)
- **Message queue processing** for WhatsApp messages
- **Integration with WhatsApp Business service**
- **Asynchronous message delivery**
- **Error handling and retry logic**

### Technology Stack
- **Backend**: FastAPI with async/await support across all services
- **Database**: PostgreSQL with SQLAlchemy ORM and async support
- **Authentication**: JWT-based auth with role-based access control
- **Message Queue**: RabbitMQ (Pika) for inter-service communication
- **Caching**: Redis for rate limiting and session management
- **AI/ML**: Pinecone for vector search, OpenAI for content generation
- **File Storage**: AWS S3 for contracts and media files
- **Email**: SMTP integration with aiosmtplib for async delivery
- **Communication**: WhatsApp Business API for direct messaging
- **Process Management**: Threading-based service orchestration

### Project Structure
```
Backend/
├── app/                  # Main FastAPI application
│   ├── auth/            # JWT authentication handlers
│   ├── middlewares/     # Rate limiting and security
│   ├── models/          # SQLAlchemy database models
│   │   ├── user.py         # User and creator models
│   │   ├── campaign.py     # Campaign management
│   │   ├── creator.py      # Creator profiles
│   │   ├── contract.py     # Contract generation
│   │   ├── payment.py      # Payment processing
│   │   ├── negotiation.py  # Negotiation workflow
│   │   └── ...
│   ├── routers/         # FastAPI route handlers
│   │   ├── auth.py         # Authentication endpoints
│   │   ├── campaigns.py    # Campaign management
│   │   ├── creators.py     # Creator operations
│   │   └── ...
│   ├── schemas/         # Pydantic request/response models
│   ├── services/        # Business logic and external APIs
│   │   ├── email_service.py    # Email integration
│   │   ├── pinecone_service.py # AI search service
│   │   └── ...
│   ├── utils/           # Utility functions and helpers
│   ├── tests/           # Unit and integration tests
│   ├── config.py        # Application configuration
│   ├── database.py      # Database connection setup
│   ├── dependencies.py  # FastAPI dependencies
│   └── main.py          # FastAPI application entry point
├── micro_services/       # Microservices directory
│   ├── whatsapp_business/   # WhatsApp Business API Service
│   │   ├── main.py             # FastAPI app for WhatsApp
│   │   ├── run_service.py      # Individual service runner
│   │   └── __init__.py
│   ├── emailing_service/    # Email Processing Service
│   │   ├── consumer.py         # RabbitMQ consumer
│   │   ├── processor.py        # Email processing logic
│   │   ├── email_helper.py     # Email utilities
│   │   ├── run_consumer.py     # Individual consumer runner
│   │   └── __init__.py
│   └── whatsapp_service/    # WhatsApp Message Service
│       ├── consumer.py         # Message queue consumer
│       ├── whatsapp_helper.py  # WhatsApp utilities
│       ├── run_consumer.py     # Individual consumer runner
│       └── __init__.py
├── helpers/              # Shared utilities
│   ├── queue_helper.py      # RabbitMQ connection helper
│   └── __init__.py
├── requirements.txt      # Python dependencies
├── run.py               # Complete system orchestrator
├── start_services.py    # Individual service manager
├── .env.example         # Environment variables template
├── firebase_auth_creds.json # Firebase authentication
├── ai_assistant.py      # AI assistant integration
├── test.py             # System testing script
└── README.md           # This documentation
```

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Redis (for rate limiting and caching)
- RabbitMQ (for message queuing between services)

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd Backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
copy .env.example .env  # On Windows
# cp .env.example .env  # On Linux/Mac
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb Influency

# Update DATABASE_URL in .env file
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/Influency
```

### 4. Message Queue Setup

```bash
# Install and start RabbitMQ
# On Windows (with Chocolatey):
choco install rabbitmq

# Start RabbitMQ service
rabbitmq-server

# RabbitMQ Management Interface will be available at:
# http://localhost:15672 (guest/guest)
```

### 4. Environment Configuration

Update the `.env` file with your configuration:

```bash
# Core Application Settings
SECRET_KEY=your-super-secret-jwt-key
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/Influency
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Microservice Ports
WHATSAPP_BUSINESS_PORT=8001
EMAIL_SERVICE_PORT=8002
WHATSAPP_SERVICE_PORT=8003

# Message Queue (RabbitMQ)
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# AI & Search Integration
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=your-environment
PINECONE_INDEX_NAME=Influency-creators
OPENAI_API_KEY=your-openai-key

# File Storage (AWS S3)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
S3_BUCKET_NAME=your-bucket-name

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@domain.com
SMTP_PASSWORD=your-app-password

# WhatsApp Business API
WHATSAPP_BUSINESS_ACCOUNT_ID=your-business-account-id
WHATSAPP_ACCESS_TOKEN=your-access-token
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id

# Redis (Optional)
REDIS_URL=redis://localhost:6379/0
```

### 5. Run the Complete System

#### Option 1: Start All Services Together (Recommended)
```bash
# Start the complete system with all microservices
python run.py
```

This will start:
- **Main API** on http://localhost:8000
- **WhatsApp Business Service** on http://localhost:8001
- **Email Service Consumer** (background process)
- **WhatsApp Service Consumer** (background process)

#### Option 2: Start Individual Services
```bash
# Start only the main API
python start_services.py main

# Start only WhatsApp Business service
python start_services.py whatsapp-business

# Start only email consumer
python start_services.py email-consumer

# Start only WhatsApp consumer
python start_services.py whatsapp-consumer

# List all available services
python start_services.py --list
```

#### Option 3: Manual Service Management
```bash
# Start individual microservices manually
python micro_services/whatsapp_business/run_service.py
python micro_services/emailing_service/run_consumer.py
python micro_services/whatsapp_service/run_consumer.py

# Start main API
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 🌐 Service Endpoints

After starting the system, the following endpoints will be available:

#### Main API Server (Port 8000)
- **API Server**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

#### WhatsApp Business Service (Port 8001)
- **WhatsApp API**: http://localhost:8001
- **WhatsApp Docs**: http://localhost:8001/docs
- **Webhook Endpoint**: http://localhost:8001/webhook

#### Background Services
- **Email Service Consumer**: Running as background process
- **WhatsApp Service Consumer**: Running as background process
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)

## 📚 API Documentation

### 🔐 Authentication Endpoints
- `POST /auth/register/user` - Register campaign manager
- `POST /auth/register/creator` - Register influencer/creator
- `POST /auth/login` - Login (supports both user types)
- `GET /auth/me` - Get current user profile
- `POST /auth/refresh` - Refresh JWT token

### 👥 Creator Management
- `GET /creators/search` - AI-powered creator search with filters
- `GET /creators/` - List all creators with pagination
- `GET /creators/{id}` - Get specific creator profile
- `PUT /creators/me` - Update creator profile
- `POST /creators/me/portfolio` - Upload portfolio items

### 📋 Campaign Management
- `POST /campaigns/` - Create new campaign
- `GET /campaigns/` - List user campaigns with filters
- `GET /campaigns/{id}` - Get campaign details
- `PUT /campaigns/{id}` - Update campaign information
- `DELETE /campaigns/{id}` - Delete campaign
- `POST /campaigns/{id}/invite` - Invite creator to campaign
- `GET /campaigns/{id}/analytics` - Get campaign performance

### 🤝 Creator Campaign Interactions
- `GET /creators/me/campaigns` - Get creator's campaigns
- `POST /creators/me/campaigns/{id}/accept` - Accept campaign invitation
- `POST /creators/me/campaigns/{id}/decline` - Decline invitation
- `POST /creators/me/campaigns/{id}/negotiate` - Start negotiation
- `GET /creators/me/campaigns/{id}/contract` - Download contract

### 📄 Contract & Payment Endpoints
- `GET /contracts/{id}` - Get contract details
- `POST /contracts/{id}/sign` - Digitally sign contract
- `GET /payments/` - List payments with status
- `POST /payments/{id}/process` - Process payment

### 📊 Analytics & Reporting
- `GET /analytics/campaigns` - Campaign performance metrics
- `GET /analytics/creators` - Creator performance analytics
- `GET /analytics/revenue` - Revenue and ROI reports

### 📱 WhatsApp Business API (Port 8001)
- `POST /whatsapp/send` - Send WhatsApp message
- `GET /whatsapp/status/{message_id}` - Check message status
- `POST /webhook` - WhatsApp webhook for incoming messages
- `GET /whatsapp/templates` - List message templates

## 🔧 Advanced Configuration

### 🤖 AI-Powered Search (Pinecone)
To enable semantic creator search:

1. Sign up for [Pinecone](https://www.pinecone.io/)
2. Create an index with dimension 384 (for sentence-transformers)
3. Add credentials to `.env`:
```bash
PINECONE_API_KEY=your-api-key
PINECONE_ENVIRONMENT=your-environment
PINECONE_INDEX_NAME=Influency-creators
```

### ☁️ File Storage (AWS S3)
For contract and media file storage:

1. Create an S3 bucket with appropriate CORS settings
2. Create IAM user with S3 permissions
3. Add credentials to `.env`:
```bash
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET_NAME=your-bucket-name
AWS_REGION=us-east-1
```

### 📧 Email Automation Configuration
Configure SMTP settings for automated emails:

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true
EMAIL_FROM_NAME=Influency
EMAIL_FROM_ADDRESS=noreply@Influency.com
```

### 📱 WhatsApp Business API Setup
1. Create a WhatsApp Business Account
2. Set up WhatsApp Business API
3. Configure webhook URL: `http://your-domain.com:8001/webhook`
4. Add credentials to `.env`:
```bash
WHATSAPP_BUSINESS_ACCOUNT_ID=your-business-account-id
WHATSAPP_ACCESS_TOKEN=your-access-token
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your-verify-token
```

### 🐰 RabbitMQ Message Queue
Configure message queuing for inter-service communication:

```bash
RABBITMQ_URL=amqp://username:password@localhost:5672/
RABBITMQ_EXCHANGE=Influency
EMAIL_QUEUE=email_queue
WHATSAPP_QUEUE=whatsapp_queue
```

### 🚀 Production Deployment
For production environments:

```bash
# Security
SECRET_KEY=your-super-secure-production-key
DEBUG=false
ALLOWED_HOSTS=your-domain.com,api.your-domain.com

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@db-host:5432/production_db

# SSL/TLS
USE_HTTPS=true
SSL_CERT_PATH=/path/to/cert.pem
SSL_KEY_PATH=/path/to/key.pem

# Monitoring
LOG_LEVEL=info
SENTRY_DSN=your-sentry-dsn
```

## 🧪 Testing the Platform

### 1. System Health Check
```bash
# Check if all services are running
curl http://localhost:8000/health
curl http://localhost:8001/docs

# Check RabbitMQ management interface
# Visit: http://localhost:15672 (guest/guest)
```

### 2. Register Users
```bash
# Register a campaign manager
curl -X POST "http://localhost:8000/auth/register/user" \
-H "Content-Type: application/json" \
-d '{
  "email": "manager@company.com",
  "username": "manager1",
  "password": "password123",
  "full_name": "John Manager",
  "company_name": "TechCorp"
}'

# Register a creator
curl -X POST "http://localhost:8000/auth/register/creator" \
-H "Content-Type: application/json" \
-d '{
  "email": "creator@example.com",
  "username": "creator1",
  "password": "password123",
  "full_name": "Jane Creator",
  "category": "tech",
  "instagram_followers": 50000,
  "youtube_subscribers": 25000
}'
```

### 3. Authentication & Search
```bash
# Login and get JWT token
curl -X POST "http://localhost:8000/auth/login" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=manager1&password=password123"

# Use the token for authenticated requests
export TOKEN="your-jwt-token-here"

# Search creators with AI-powered semantic search
curl -H "Authorization: Bearer $TOKEN" \
"http://localhost:8000/creators/search?query=tech+lifestyle&min_followers=10000&limit=5"
```

### 4. Campaign Creation & Management
```bash
# Create a new campaign
curl -X POST "http://localhost:8000/campaigns/" \
-H "Authorization: Bearer $TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "title": "Summer Tech Campaign 2024",
  "brand_name": "TechCorp",
  "campaign_type": "product_launch",
  "budget": 15000,
  "start_date": "2024-07-01T00:00:00",
  "end_date": "2024-07-31T23:59:59",
  "description": "Launch campaign for our new tech product"
}'

# Invite creator to campaign
curl -X POST "http://localhost:8000/campaigns/1/invite" \
-H "Authorization: Bearer $TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "creator_id": 1,
  "message": "We would love to collaborate with you!"
}'
```

### 5. Testing Message Services
```bash
# Test WhatsApp Business API (if configured)
curl -X POST "http://localhost:8001/whatsapp/send" \
-H "Content-Type: application/json" \
-d '{
  "to": "+1234567890",
  "message": "Hello from Influency!",
  "template_name": "welcome_message"
}'

# Test email service by triggering an email
# This will be processed by the email consumer service
curl -X POST "http://localhost:8000/campaigns/1/invite" \
-H "Authorization: Bearer $TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "creator_id": 1,
  "send_email": true
}'
```

### 6. Run Automated Tests
```bash
# Run the test suite
python -m pytest app/tests/ -v

# Run specific test modules
python app/tests/email.py
python app/tests/pinecone.py
python app/tests/queue.py

# Test individual components
python test.py
```

## 🔒 Security Features

- **JWT Authentication** with configurable expiration and refresh tokens
- **Role-based Access Control** (Campaign Managers vs Creators)
- **Rate Limiting** with Redis to prevent API abuse
- **Input Validation** using Pydantic schemas with custom validators
- **CORS Protection** with configurable origins
- **SQL Injection Protection** via SQLAlchemy ORM and parameterized queries
- **Password Hashing** using bcrypt with salt rounds
- **Request Size Limiting** to prevent DoS attacks
- **HTTPS Enforcement** in production environments
- **API Key Management** for external service integrations
- **Webhook Signature Verification** for WhatsApp callbacks

## 📈 Scalability & Performance Features

### 🔄 Asynchronous Processing
- **Async/Await** throughout all services for high concurrency
- **Database Connection Pooling** with SQLAlchemy async engine
- **Non-blocking I/O** for all external API calls
- **Background Task Processing** with message queues

### 🏗️ Microservices Architecture
- **Service Isolation** for independent scaling and deployment
- **Message Queue Communication** for reliable inter-service messaging
- **Distributed Processing** across multiple service instances
- **Independent Database Connections** per service

### 📊 Monitoring & Observability
- **Structured Logging** with configurable log levels
- **Health Check Endpoints** for all services
- **Performance Metrics** collection
- **Error Tracking** with detailed stack traces
- **Request Tracing** across service boundaries

### 🚀 Deployment Ready
- **Docker Support** with multi-stage builds
- **Horizontal Scaling** ready with stateless design
- **Load Balancer Compatible** with session-free architecture
- **Environment-based Configuration** for different deployment stages
- **Database Migration Support** with Alembic

## 🐳 Docker Deployment (Optional)

### Build and Run with Docker
```bash
# Build the main application
docker build -t Influency-api .

# Build microservices
docker build -t Influency-whatsapp -f micro_services/whatsapp_business/Dockerfile .
docker build -t Influency-email -f micro_services/emailing_service/Dockerfile .

# Run with Docker Compose
docker-compose up -d

# Or run individual containers
docker run -d -p 8000:8000 --name Influency-api Influency-api
docker run -d -p 8001:8001 --name Influency-whatsapp Influency-whatsapp
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Module Import Errors
```bash
# Ensure Python path is set correctly
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# On Windows
set PYTHONPATH=%PYTHONPATH%;%cd%
```

#### 2. Database Connection Issues
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Verify database exists
psql -h localhost -U username -l
```

#### 3. RabbitMQ Connection Issues
```bash
# Check RabbitMQ status
rabbitmqctl status

# Restart RabbitMQ service
# Windows: net stop RabbitMQ && net start RabbitMQ
# Linux: sudo systemctl restart rabbitmq-server
```

#### 4. Port Conflicts
```bash
# Check what's running on ports
netstat -an | findstr "8000 8001"  # Windows
# lsof -i :8000,8001  # Linux/Mac

# Kill processes if needed
taskkill /F /PID <process_id>  # Windows
# kill -9 <process_id>  # Linux/Mac
```

#### 5. Service Startup Issues
```bash
# Check individual service logs
python micro_services/whatsapp_business/run_service.py
python micro_services/emailing_service/run_consumer.py

# Verify environment variables are loaded
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('DATABASE_URL'))"
```

### Logs and Debugging
```bash
# Enable debug mode
export DEBUG=true

# Check application logs
tail -f logs/app.log

# Monitor RabbitMQ queues
rabbitmqctl list_queues

# Check database connections
python -c "from app.database import get_database; print('DB connection successful')"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write unit tests for new features
- Update documentation for API changes
- Use type hints throughout the codebase
- Implement proper error handling and logging

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support & Documentation

### Getting Help
- **API Documentation**: Visit `/docs` endpoint for interactive Swagger UI
- **Service Status**: Check `/health` endpoints for service health
- **Issue Tracking**: Create issues in the repository for bugs/features
- **Community**: Join our community discussions

### Additional Resources
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLAlchemy Async Guide**: https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html
- **RabbitMQ Tutorials**: https://www.rabbitmq.com/tutorials.html
- **Pinecone Documentation**: https://docs.pinecone.io/
- **WhatsApp Business API**: https://developers.facebook.com/docs/whatsapp

### Architecture Diagrams
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Load Balancer │    │   API Gateway   │
│   (React/Vue)   │◄──►│   (Nginx/HAProxy│◄──►│   (Optional)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                       ┌────────────────────────────────┴────────────────────────────────┐
                       │                                                                 │
                       ▼                                                                 ▼
            ┌─────────────────┐                                              ┌─────────────────┐
            │   Main API      │                                              │  WhatsApp API   │
            │   (Port 8000)   │                                              │  (Port 8001)    │
            │   FastAPI       │                                              │   FastAPI       │
            └─────────────────┘                                              └─────────────────┘
                       │                                                                 │
                       │                                                                 │
                       ▼                                                                 ▼
            ┌─────────────────┐    ┌─────────────────┐                      ┌─────────────────┐
            │   PostgreSQL    │    │   Redis Cache   │                      │  Message Queue  │
            │   Database      │    │   Rate Limiting │                      │   (RabbitMQ)    │
            └─────────────────┘    └─────────────────┘                      └─────────────────┘
                                                                                        │
                       ┌────────────────────────────────────────────────────────────────┘
                       │                                          │
                       ▼                                          ▼
            ┌─────────────────┐                        ┌─────────────────┐
            │  Email Service  │                        │ WhatsApp Service│
            │   Consumer      │                        │   Consumer      │
            │  (Background)   │                        │  (Background)   │
            └─────────────────┘                        └─────────────────┘
                       │                                          │
                       ▼                                          ▼
            ┌─────────────────┐                        ┌─────────────────┐
            │   SMTP Server   │                        │ WhatsApp Business│
            │   (Gmail/AWS)   │                        │      API        │
            └─────────────────┘                        └─────────────────┘
```

---

**Built with ❤️ using FastAPI, SQLAlchemy, RabbitMQ, and modern Python async patterns**

*Influency - Connecting Brands with Creators through Intelligent Automation*

