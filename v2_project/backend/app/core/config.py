"""
Configuration module for Alsakr V2 Industrial AI Platform
Centralized settings for all services and components
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_CORS_ORIGINS: list = ["*"]
    
    # Elasticsearch Settings
    ES_HOST: str = os.getenv("ES_HOST", "localhost")
    ES_PORT: int = 9200
    ES_PRODUCTS_INDEX: str = "sick_products"
    ES_PDF_INDEX: str = "sick_datasheets"
    
    # Qdrant Settings
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = 6333
    QDRANT_PRODUCTS_COLLECTION: str = "sick_products_vectors"
    QDRANT_PDF_COLLECTION: str = "sick_datasheets_vectors"
    QDRANT_VECTOR_SIZE: int = 768  # nomic-embed-text dimension
    
    # Ollama Settings
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"
    OLLAMA_CHAT_MODEL: str = "llama3.2"
    
    # PocketBase Settings
    PB_URL: str = os.getenv("PB_URL", "http://localhost:8090")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@alsakronline.com")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "password123")
    
    # SMTP Settings (Hostinger)
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.hostinger.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "465"))
    SMTP_USER: str = os.getenv("SMTP_USER", "admin@alsakronline.com")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "password123")
    EMAILS_FROM_EMAIL: str = os.getenv("EMAILS_FROM_EMAIL", "admin@alsakronline.com")
    EMAILS_FROM_NAME: str = os.getenv("EMAILS_FROM_NAME", "Alsakr Online")
    
    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # Data Settings
    DATA_DIR: str = os.getenv("DATA_DIR", "/data")
    PRODUCTS_CSV: str = "products.csv"
    IMAGES_DIR: str = "scraped_data/images"
    PDF_DOWNLOAD_DIR: str = "pdfs"
    
    # Processing Settings
    BATCH_SIZE: int = 50  # For embeddings
    PDF_CHUNK_SIZE: int = 1000  # Characters per chunk
    PDF_CHUNK_OVERLAP: int = 200
    MAX_RETRIES: int = 3
    TIMEOUT: int = 30  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_es_url() -> str:
    """Get Elasticsearch connection URL"""
    return f"http://{settings.ES_HOST}:{settings.ES_PORT}"


def get_qdrant_url() -> str:
    """Get Qdrant connection URL"""  
    return f"http://{settings.QDRANT_HOST}:{settings.QDRANT_PORT}"


def get_products_csv_path() -> str:
    """Get full path to products CSV file"""
    return os.path.join(settings.DATA_DIR, settings.PRODUCTS_CSV)


def get_images_dir_path() -> str:
    """Get full path to images directory"""
    return os.path.join(settings.DATA_DIR, settings.IMAGES_DIR)


def get_pdf_dir_path() -> str:
    """Get full path to PDF download directory"""
    pdf_dir = os.path.join(settings.DATA_DIR, settings.PDF_DOWNLOAD_DIR)
    os.makedirs(pdf_dir, exist_ok=True)
    return pdf_dir
