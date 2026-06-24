import pytest
from langchain_core.messages import SystemMessage, HumanMessage
from src.database.brain_database import AtlasBrain
from src.brain.model_manager import AtlasModelManager
from config.settings import settings
from config.logger import logger

@pytest.mark.asyncio
async def test_atlas_chat_history_integration():
    """
    Refined integration test to ensure that local models (Ollama)
    perfectly comprehend the injected short-term message history context.
    """
    logger.info("=== Starting Refined Semantic Memory Integration Test ===")
    
    brain = AtlasBrain()
    await brain.initialize_db()
    manager = AtlasModelManager()
    
    session_id = "test_memory_session_2026"
    await brain.clear_session_history(session_id=session_id)
    
    logger.debug("Populating database layer with artificial memory context...")
    await brain.add_message(role="human", content="ATLAS, take note: my operational codename on this terminal is Root-Alpha.", session_id=session_id)
    await brain.add_message(role="ai", content="Understood, Sir. The codename Root-Alpha has been securely stored locally within my core systems.", session_id=session_id)
    
    raw_history = await brain.get_chat_history(session_id=session_id, limit=10)
    
    formatted_history = ""
    for msg in raw_history:
        speaker = "User (Root)" if msg["role"] == "human" else "ATLAS (You)"
        formatted_history += f"[{speaker}]: {msg['content']}\n"
    
    base_system = settings.SYSTEM_PROMPT.format(mood_humor="30%")
    
    enriched_system_prompt = (
            f"{base_system}\n\n"
            f"CONTEXT OF PREVIOUS CONVERSATION (RECENT MEMORY):\n"
            f"Use the historical timeline below to recall names, commands, or prior facts:\n"
            f"-------\n"
            f"{formatted_history}"
            f"-------\n"
            f"CRITICAL DIRECTIVE: Do not invoke any system tools or diagnostics for this query. "
            f"Answer the new user query directly below using only the historical data provided."
        )
    
    new_input = "What is my operational codename again? Confirm it for me."
    
    langchain_messages = [
        SystemMessage(content=enriched_system_prompt),
        HumanMessage(content=new_input)
    ]
    
    logger.info("Dispatching payload containing structured memory timeline to AI engine...")
    
    response = await manager.invoke_with_fallback(langchain_messages)
    
    await brain.add_message(role="ai", content=response, session_id=session_id)
    
    print(f"\n\n[ATLAS INTEGRATED RESPONSE]: {response}\n")
    
    assert response is not None
    assert "Root-Alpha" in response, "ATLAS failed to extract and recall the operational codename from the structured history."
    
    logger.info("=== Semantic Memory Context Integration Test Completed Successfully ===")