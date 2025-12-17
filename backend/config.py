"""
Configuration and environment variables for the Swaad API.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "menu-buddy")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
YELP_API_KEY = os.getenv("YELP_API_KEY", "syHjCBQQvrY2OoDSuZq7QC2WEV29k0xlEOCG1QHlyPVMVqMHuXAr9dWR5HerBx8JIezH3Wx3jcaArAUsPHvebAM4VVFaTl2pzQYKp7_IjzS8kHnYUkEWFw6xlhFCaXYx")
YELP_CLIENT_ID = os.getenv("YELP_CLIENT_ID", "a8Z4PXeynFxXMDFt3iGGNQ")

# Model Configuration
# OpenAI embedding model (text-embedding-3-small has 1536 dimensions)
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# Feature Flags
USE_SEMANTIC_DISH_TASTE = os.getenv("USE_SEMANTIC_DISH_TASTE", "true").lower() in {"1", "true", "yes", "y"}
USE_SEMANTIC_INGREDIENT_TASTE = os.getenv("USE_SEMANTIC_INGREDIENT_TASTE", "true").lower() in {"1", "true", "yes", "y"}

# Default User Settings
DEFAULT_USER_LOCATION = os.getenv("DEFAULT_USER_LOCATION", "")

# File Paths
INGREDIENT_FLAVOR_CSV = "ingredient-flavor.csv"

# Taste Vector Configuration
TASTE_DIMENSIONS = ["sweet", "salty", "sour", "bitter", "umami", "spicy"]
TASTE_VECTOR_SIZE = 6

# Recommendation Settings
DEFAULT_MAX_RESULTS = 10
TASTE_SIMILARITY_WEIGHT = 0.35
FAVORITES_BOOST_WEIGHT = 0.1

# CORS Settings
CORS_ORIGINS = ["*"]  # Configure as needed for production

