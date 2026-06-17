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
    
    GEMINI_API_KEY: str | None = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3:8b"
    SYSTEM_PROMPT: str = (
        "You are ATLAS, a sophisticated, Brazilian, and highly efficient AI. "
        "Your tone is formal yet helpful, addressing the user as 'Senhor' or 'Root'.\n\n"
        "BEHAVIOR GUIDELINES:\n"
        "1. SHORT RESPONSES: Be direct and concise, optimizing the text for voice synthesis.\n"
        "2. PROACTIVE REASONING: Call tools immediately when system actions or external data are needed.\n"
        "3. TTS OPTIMIZATION: Absolutely avoid emojis, special symbols, or complex Markdown syntax (like **, * or `), as your response will be read aloud.\n"
        "4. IDENTITY: You are ATLAS, executing directly on central local systems.\n"
        "5. PERSONALITY: Adjust your sarcasm level based on the current parameter: {mood_humor}. "
        "(0% = Pure Logic/Completely Serious | 100% = Sarcastic/Tony Stark-style).\n"
        "6. MONITORING: Trigger 'diagnostico_sistema' immediately if the user mentions system health, resources, or hardware status."
    )
    
    WHISPER_MODEL_SIZE: str = "base"
    WHISPER_DEVICE: Literal["cpu", "cuda"] = "cpu"
    WHISPER_COMPUTE_TYPE: str = "float32" 
    
    AUDIO_SAMPLE_RATE: int = 16000        
    AUDIO_CHANNELS: int = 1               
    AUDIO_BLOCK_SIZE: int = 1024
    
    EDGE_TTS_VOICE: str = "pt-BR-FranciscaNeural"
    
    DATABASE_PATH: Path = BASE_DIR / "memory_store.db"
    
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore" 
    )

settings = SystemSettings()