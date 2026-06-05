from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class SystemSettings(BaseSettings):
    """
    Gerenciador central de configurações e parâmetros padrões da ATLAS.
    O Pydantic valida os tipos automaticamente em tempo de execução.
    """

    ENVIRONMENT: Literal["development", "production", "testing"] = "development"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    BASE_PATH: Path = BASE_DIR
    
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3:8b"
    SYSTEM_PROMPT: str = "Você é ATLAS, uma inteligência artificial local focada em segurança, automação e suporte técnico. Seja concisa, precisa e profissional."
    
    WHISPER_MODEL_SIZE: str = "base"
    WHISPER_DEVICE: Literal["cpu", "cuda"] = "cpu"
    WHISPER_COMPUTE_TYPE: str = "float32" 
    
    AUDIO_SAMPLE_RATE: int = 16000        
    AUDIO_CHANNELS: int = 1               
    AUDIO_BLOCK_SIZE: int = 1024
    
    EDGE_TTS_VOICE: str = "pt-BR-AntonioNeural" 
    
    DATABASE_PATH: Path = BASE_DIR / "memory_store.db"
    
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore" 
    )