import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from backend directory
ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / '.env')

# Centralized settings
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "nvidia")
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "")
NVIDIA_BASE_URL = os.environ.get("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_MODEL = os.environ.get("NVIDIA_MODEL", "meta/llama-3.1-70b-instruct")

# Backward compatibility mapping
MODEL_NAME = NVIDIA_MODEL
API_KEY = NVIDIA_API_KEY
BASE_URL = NVIDIA_BASE_URL

# Generation parameters
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.4"))
TOP_P = float(os.environ.get("TOP_P", "0.7"))
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "1024"))
STREAM = os.environ.get("STREAM", "true").lower() in ("true", "1", "yes")
TIMEOUT = int(os.environ.get("TIMEOUT", "60"))

# Retrieval settings
TOP_K = int(os.environ.get("TOP_K", "5"))
RERANK_TOP_K = int(os.environ.get("RERANK_TOP_K", "3"))
CONFIDENCE_THRESHOLD = float(os.environ.get("CONFIDENCE_THRESHOLD", "0.45"))

# Embedding parameters
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5")

# Paths
VECTOR_DB_PATH = os.path.abspath(os.path.join(ROOT_DIR, os.environ.get("VECTOR_DB_PATH", "vector_store.db")))
SQLITE_DB_PATH = os.path.abspath(os.path.join(ROOT_DIR, os.environ.get("SQLITE_DB_PATH", "analytics.db")))

# Environment flags
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
DEBUG = os.environ.get("DEBUG", "true").lower() in ("true", "1", "yes")
