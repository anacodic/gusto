"""
Swaad Recipe Recommendation API - Main Application
Modularized version with clean separation of concerns.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS, SENTENCE_TRANSFORMER_MODEL, GROQ_API_KEY
from integrations.embeddings import get_embedding_model
from services.restaurant_service import get_groq_client
from models import ChatRequest
from routes.chat import chat_endpoint
from routes import users, friends, groups, collections, restaurants
from recipe_database import load_recipes_database
from db import init_db


# Initialize FastAPI app
app = FastAPI(title="Swaad Recipe Recommendation API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(friends.router)
app.include_router(groups.router)
app.include_router(collections.router)
app.include_router(restaurants.router)


@app.on_event("startup")
async def startup():
    """Preload models and initialize database on startup."""
    # Initialize database
    print("Initializing database...")
    await init_db()
    print("Database initialized.")
    
    # Preload models (optional - skip if sentence-transformers not installed)
    try:
        print(f"Preloading sentence-transformer model: {SENTENCE_TRANSFORMER_MODEL}")
        get_embedding_model()
        print("Sentence-transformer model loaded.")
    except ImportError as e:
        print(f"⚠️ Sentence-transformer model not available: {e}")
        print("⚠️ Some features may be limited. Install with: pip install sentence-transformers")

    if GROQ_API_KEY:
        get_groq_client()
        print("Groq client initialized.")

    # Load recipe database (231K recipes)
    print("Loading recipe database...")
    load_recipes_database()
    print("Recipe database loaded.")


@app.get("/")
def read_root():
    """Root endpoint - API health check."""
    return {"message": "Swaad Recipe Recommendation API is running"}


@app.post("/api/chat")
async def chat_with_restaurants(request: ChatRequest):
    """
    Chat endpoint for restaurant recommendations.
    
    This endpoint:
    1. Takes a natural language query from the user
    2. Uses Pinecone for semantic search of restaurants
    3. Ranks results based on taste similarity and user preferences
    4. Returns personalized restaurant and dish recommendations
    """
    return await chat_endpoint(request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

