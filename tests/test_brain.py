import pytest
from langchain_core.messages import SystemMessage, HumanMessage
from src.brain.model_manager import AtlasModelManager
from config.settings import settings
from config.logger import logger

@pytest.mark.asyncio
async def test_atlas_brain_routing():
    """
    Integration test to validate the dynamic routing mechanics of ATLAS.
    Ensures that local Ollama handles the context or Gemini seamlessly falls back.
    """
    logger.info("=== Starting Brain Engine Integration Test (AI Architecture) ===")
    
    manager = AtlasModelManager()
    
    system_instruction = settings.SYSTEM_PROMPT.format(mood_humor="30%")
    
    messages = [
        SystemMessage(content=system_instruction),
        HumanMessage(content="ATLAS, execute an internal ping and confirm your current active operational model.")
    ]
    
    logger.info("Dispatching test payload to Model Manager interface...")
    
    response = await manager.invoke_with_fallback(messages)
    
    assert response is not None, "The AI core response layer cannot evaluate to Null."
    assert len(response.strip()) > 0, "The AI model returned an unexpected empty string context."
    
    print(f"\n\n[ATLAS RESPONSE]: {response}\n")
    logger.info("=== AI Core Model Routing Integration Test Completed Successfully ===")