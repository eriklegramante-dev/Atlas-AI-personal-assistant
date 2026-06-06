import pytest
from langchain_core.messages import SystemMessage, HumanMessage
from src.brain.model_manager import AtlasModelManager
from config.settings import settings
from config.logger import logger

@pytest.mark.asyncio
async def test_atlas_brain_routing():
    """
    Teste de integração para validar o roteamento dinâmico da ATLAS.
    Garante que o Ollama responda ou que o Gemini assuma em caso de falha.
    """
    logger.info("=== Iniciando Teste de Integração do Cérebro (IA) ===")
    
    manager = AtlasModelManager()
    
    system_instruction = settings.SYSTEM_PROMPT.format(mood_humor="30%")
    
    messages = [
        SystemMessage(content=system_instruction),
        HumanMessage(content="ATLAS, execute um ping interno e confirme seu modelo operacional atual.")
    ]
    
    logger.info("Enviando comando de teste para o Model Manager...")
    
    response = await manager.invoke_with_fallback(messages)
    
    assert response is not None, "A resposta da IA não pode ser nula."
    assert len(response.strip()) > 0, "A IA retornou uma string vazia."
    
    print(f"\n\n[ATLAS RESPONSE]: {response}\n")
    logger.info("=== Teste de Roteamento de IA Concluído com Sucesso ===")