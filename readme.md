# 🚀 InfluenceFlow - End-to-End Influencer Marketing Automation Platform

InfluenceFlow is a comprehensive FastAPI-based backend platform that automates the entire influencer marketing workflow from creator discovery to campaign completion and payment processing.

## ✨ Key Features

### 🔍 AI-Powered Creator Discovery
- **Vector-based search** using Pinecone for semantic creator matching
- **Advanced filtering** by follower count, engagement rate, location, category
- **Multi-platform support** (Instagram, YouTube, TikTok, Twitter)

### 📧 Automated Outreach & Communication
- **Email automation** for campaign invitations and notifications
- **WhatsApp integration** support for direct creator communication
- **Template-based messaging** with personalization

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

### Technology Stack
- **Backend**: FastAPI with async/await support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT-based auth with role-based access
- **Caching**: Redis for rate limiting and session management
- **AI/ML**: Pinecone for vector search, OpenAI for content generation
- **File Storage**: AWS S3 for contracts and media files
- **Email**: SMTP integration with template support

### Project Structure
```
Backend/
├── app/
│   ├── auth/              # JWT authentication handlers
│   ├── middlewares/       # Rate limiting and security
│   ├── models/           # SQLAlchemy database models
│   ├── routers/          # FastAPI route handlers
│   ├── schemas/          # Pydantic request/response models
│   ├── services/         # Business logic and external APIs
│   ├── utils/            # Utility functions and helpers
│   ├── config.py         # Application configuration
│   ├── database.py       # Database connection setup
│   ├── dependencies.py   # FastAPI dependencies
│   └── main.py           # FastAPI application entry point
├── requirements.txt      # Python dependencies
├── run.py               # Application runner script
├── .env.example         # Environment variables template
└── README.md           # This documentation
```

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Redis (optional, for rate limiting)

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd Backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb influenceflow

# Update DATABASE_URL in .env file
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/influenceflow
```

### 4. Environment Configuration

Update the `.env` file with your configuration:

```bash
# Required settings
SECRET_KEY=your-super-secret-jwt-key
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/influenceflow

# Optional integrations
PINECONE_API_KEY=your-pinecone-key  # For AI-powered search
AWS_ACCESS_KEY_ID=your-aws-key      # For file storage
SMTP_USERNAME=your-email@domain.com # For email automation
```

### 5. Run the Application

```bash
# Start the server
python run.py

# Or with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Server**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 📚 API Documentation

### Authentication Endpoints
- `POST /auth/register/user` - Register campaign manager
- `POST /auth/register/creator` - Register influencer/creator
- `POST /auth/login` - Login (supports both user types)
- `GET /auth/me` - Get current user profile

### Creator Management
- `GET /creators/search` - AI-powered creator search
- `GET /creators/` - List all creators
- `GET /creators/{id}` - Get creator profile
- `PUT /creators/me` - Update creator profile

### Campaign Management
- `POST /campaigns/` - Create new campaign
- `GET /campaigns/` - List user campaigns
- `GET /campaigns/{id}` - Get campaign details
- `PUT /campaigns/{id}` - Update campaign
- `POST /campaigns/{id}/invite` - Invite creator to campaign

### Creator Campaign Interactions
- `GET /creators/me/campaigns` - Get creator's campaigns
- `POST /creators/me/campaigns/{id}/accept` - Accept invitation
- `POST /creators/me/campaigns/{id}/decline` - Decline invitation

## 🔧 Advanced Configuration

### AI-Powered Search (Pinecone)
To enable semantic creator search:

1. Sign up for [Pinecone](https://www.pinecone.io/)
2. Create an index with dimension 384
3. Add credentials to `.env`:
```bash
PINECONE_API_KEY=your-api-key
PINECONE_ENVIRONMENT=your-environment
PINECONE_INDEX_NAME=influenceflow-creators
```

### File Storage (AWS S3)
For contract and media file storage:

1. Create an S3 bucket
2. Create IAM user with S3 permissions
3. Add credentials to `.env`:
```bash
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET_NAME=your-bucket-name
```

### Email Automation
For automated outreach and notifications:

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## 🧪 Testing the Platform

### 1. Register Users
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
  "instagram_followers": 50000
}'
```

### 2. Search Creators
```bash
curl "http://localhost:8000/creators/search?query=tech+lifestyle&min_followers=10000&limit=5"
```

### 3. Create Campaign and Invite Creators
```bash
# Create campaign (requires authentication)
curl -X POST "http://localhost:8000/campaigns/" \
-H "Authorization: Bearer YOUR_JWT_TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "title": "Summer Tech Campaign",
  "brand_name": "TechCorp",
  "campaign_type": "product_launch",
  "budget": 10000,
  "start_date": "2024-06-01T00:00:00",
  "end_date": "2024-06-30T23:59:59"
}'
```

## 🔒 Security Features

- **JWT Authentication** with configurable expiration
- **Rate Limiting** to prevent API abuse
- **Input Validation** using Pydantic schemas
- **CORS Protection** with configurable origins
- **SQL Injection Protection** via SQLAlchemy ORM
- **Password Hashing** using bcrypt

## 📈 Scalability Features

- **Async/Await** throughout for high concurrency
- **Database Connection Pooling** with SQLAlchemy
- **Redis Caching** for session management
- **Modular Architecture** for easy feature additions
- **API Rate Limiting** to manage load
- **Horizontal Scaling** ready with stateless design

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the `/docs` endpoint for API documentation
- Review the code examples in this README

---

**Built with ❤️ using FastAPI, SQLAlchemy, and modern Python async patterns**

