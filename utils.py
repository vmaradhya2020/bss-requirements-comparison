"""
Utility functions for the BSS requirements comparison system
"""
import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except FileNotFoundError:
        logger.warning(f"Config file not found: {config_path}, using defaults")
        return get_default_config()
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return get_default_config()


def get_default_config() -> Dict[str, Any]:
    """Return default configuration"""
    return {
        "llm": {
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.3,
            "max_tokens": 2000,
            "embedding_model": "text-embedding-ada-002"
        },
        "comparison": {
            "exact_match_threshold": 0.95,
            "similar_match_threshold": 0.70
        },
        "report": {
            "default_format": "html",
            "include_statistics": True,
            "include_recommendations": True
        },
        "output": {
            "directory": "outputs/comparison_reports"
        }
    }


def get_api_key(provider: str = "openai") -> str:
    """Get API key from environment variables"""
    key_mapping = {
        "openai": "OPENAI_API_KEY",
        "azure": "AZURE_OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY"
    }

    env_var = key_mapping.get(provider.lower(), "OPENAI_API_KEY")
    api_key = os.getenv(env_var)

    if not api_key:
        logger.warning(f"API key not found for {provider}. Set {env_var} in .env file")

    return api_key


def ensure_directory(directory: str) -> Path:
    """Ensure directory exists, create if not"""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""

    # Remove extra whitespace
    text = " ".join(text.split())

    # Remove special characters that might interfere
    text = text.strip()

    return text


def extract_filename(file_path: str) -> str:
    """Extract filename without extension"""
    return Path(file_path).stem


def format_percentage(value: float) -> str:
    """Format percentage with 1 decimal place"""
    return f"{value:.1f}%"
