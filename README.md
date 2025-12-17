# 🍽️ Gusto - Multi-Agent Restaurant Recommendation System

A sophisticated AI-powered restaurant recommendation platform that uses multi-agent orchestration, taste vector matching, and semantic search to provide personalized dining recommendations.

## ✨ Features

- **Multi-Agent System**: Orchestrated agents for Yelp integration, flavor matching, beverage pairing, and budget analysis
- **Taste Vector Matching**: 6-dimensional flavor profiles (sweet, salty, sour, bitter, umami, spicy) for personalized recommendations
- **Beer Pairing**: AI-powered beer recommendations that complement restaurant dishes
- **Vector Search**: Pinecone integration for semantic restaurant discovery
- **Group Recommendations**: Find restaurants that work for multiple people with different preferences
- **Collections**: Pinterest-style saving of favorite restaurants
- **Social Features**: Friends, groups, and shared recommendations

## 🏗️ Architecture

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Async database ORM
- **Pinecone** - Vector database for semantic search
- **AWS Cognito** - User authentication
- **Strands Framework** - Multi-agent orchestration
- **Groq** - Fast LLM inference

### Frontend
- **React** - Modern UI framework
- **Vite** - Fast build tool
- **React Router** - Client-side routing
- **AWS Cognito** - Authentication integration

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Groq API key
- Pinecone API key
- AWS Cognito User Pool

### Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Create .env file (see ENV_SETUP.md)
cp .env.example .env
# Edit .env with your API keys

# Start backend
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install

# Create .env file
cp .env.example .env
# Edit .env with your Cognito credentials

# Start frontend
npm run dev
```

See `backend/ENV_SETUP.md` for detailed environment variable configuration.

## 📁 Project Structure

```
gusto/
├── agents/              # Multi-agent system
│   ├── orchestrator.py  # Main agent coordinator
│   ├── yelp_agent.py   # Yelp API integration
│   ├── flavor_agent.py # Taste matching
│   ├── beverage_agent.py # Beer pairing
│   └── budget_agent.py # Budget analysis
├── backend/            # FastAPI backend
│   ├── routes/         # API endpoints
│   ├── services/       # Business logic
│   ├── integrations/   # External APIs
│   └── middleware/     # Auth middleware
├── frontend/           # React frontend
│   ├── src/
│   │   ├── pages/      # Page components
│   │   ├── components/ # Reusable components
│   │   └── hooks/      # Custom hooks
│   └── public/
├── data/               # Data files
└── docs/               # Documentation
```

## 🔑 Environment Variables

### Backend (.env)
- `GROQ_API_KEY` - Required for AI chat
- `PINECONE_API_KEY` - Required for vector search
- `COGNITO_USER_POOL_ID` - Required for authentication
- `AWS_REGION` - AWS region
- `DATABASE_URL` - Database connection (defaults to SQLite)

### Frontend (.env)
- `VITE_API_URL` - Backend API URL
- `VITE_COGNITO_USER_POOL_ID` - Cognito User Pool ID
- `VITE_COGNITO_CLIENT_ID` - Cognito Client ID

## 📚 API Endpoints

- `POST /api/chat` - Main recommendation endpoint
- `GET /api/restaurants/discover` - Discover feed
- `GET /api/restaurants/:id` - Restaurant details
- `GET /api/collections` - User collections
- `GET /api/groups` - User groups
- `GET /api/friends` - User friends

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/

# Frontend (add tests as needed)
cd frontend
npm test
```

## 📝 License

[Add your license here]

## 🤝 Contributing

[Add contribution guidelines here]

## 📧 Contact

[Add contact information here]
