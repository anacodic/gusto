# Environment Setup Guide for Gusto Backend

## Required Environment Variables

Create a `.env` file in the `gusto/backend/` directory with the following variables:

### Critical (Required for App to Function)

```bash
# Groq API Key - Required for AI chat
GROQ_API_KEY=your_groq_api_key_here

# Pinecone API Key - Required for vector search
PINECONE_API_KEY=your_pinecone_api_key_here

# AWS Cognito User Pool ID - Required for authentication
COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX

# AWS Region - Required for Cognito
AWS_REGION=us-east-1
```

### Optional (Have Defaults)

```bash
# Pinecone Index Name (defaults to "menu-buddy")
PINECONE_INDEX=menu-buddy

# Database URL (defaults to SQLite)
DATABASE_URL=sqlite+aiosqlite:///./swaad.db

# Sentence Transformer Model (defaults to "all-MiniLM-L6-v2")
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2

# Feature Flags (defaults to true)
USE_SEMANTIC_DISH_TASTE=true
USE_SEMANTIC_INGREDIENT_TASTE=true

# Default User Location
DEFAULT_USER_LOCATION=
```

### Optional (For Additional Features)

```bash
# Yelp API Key (only needed if using Yelp agent)
YELP_API_KEY=your_yelp_api_key_here

# Google Gemini API Key (for menu image processing)
GEMINI_API_KEY=your_gemini_api_key_here
```

## How to Get API Keys

1. **Groq API Key**: https://console.groq.com/
2. **Pinecone API Key**: https://app.pinecone.io/
3. **AWS Cognito**: AWS Console > Cognito > User Pools
4. **Yelp API**: https://www.yelp.com/developers
5. **Gemini API**: https://aistudio.google.com

## Database Initialization

The database is automatically initialized on first backend startup via `init_db()` in `main.py`. 
The SQLite database file `swaad.db` will be created automatically in the backend directory.

## Frontend Environment Variables

Create a `.env` file in the `gusto/frontend/` directory:

```bash
# Backend API URL
VITE_API_URL=http://localhost:8000

# AWS Cognito Configuration
VITE_COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
VITE_COGNITO_CLIENT_ID=your_cognito_client_id_here
```

## Quick Start

1. Copy environment variables to `.env` files
2. Install dependencies:
   ```bash
   cd gusto/backend && pip install -r requirements.txt
   cd ../frontend && npm install
   ```
3. Start backend:
   ```bash
   cd gusto/backend && uvicorn main:app --reload
   ```
4. Start frontend:
   ```bash
   cd gusto/frontend && npm run dev
   ```
