import pytest
from langchain_core.messages import SystemMessage, HumanMessage
from src.database.brain_database import AtlasBrain
from src.brain.model_manager import AtlasModelManager
from config.settings import settings
from config.logger import logger

@pytest.mark.asyncio
async def test_atlas_chat_history_integration():
    """
    Teste de integração refinado para garantir que modelos locais (Ollama)
    compreendam perfeitamente o histórico de mensagens injetado.
    """
    logger.info("=== Iniciando Teste de Integração de Memória Semântica Refinado ===")
    
    brain = AtlasBrain()
    await brain.initialize_db()
    manager = AtlasModelManager()
    
    session_id = "test_memory_session_2026"
    await brain.clear_session_history(session_id=session_id)
    
    logger.debug("Alimentando o banco com o contexto passado...")
    await brain.add_message(role="human", content="ATLAS, registre: meu codinome operacional neste terminal é Root-Alpha.", session_id=session_id)
    await brain.add_message(role="ai", content="Entendido, Senhor. O codinome Root-Alpha foi armazenado localmente nos meus sistemas de segurança.", session_id=session_id)
    
    raw_history = await brain.get_chat_history(session_id=session_id, limit=10)
    
    formatted_history = ""
    for msg in raw_history:
        speaker = "Usuário (Root)" if msg["role"] == "human" else "ATLAS (Você)"
        formatted_history += f"[{speaker}]: {msg['content']}\n"
    
    base_system = settings.SYSTEM_PROMPT.format(mood_humor="30%")
    
    enriched_system_prompt = (
        f"{base_system}\n\n"
        f"CONTEXTO DE CONVERSA ANTERIOR (MEMÓRIA RECENTE):\n"
        f"Use o histórico abaixo para lembrar de nomes, comandos ou fatos ditos antes:\n"
        f"-------\n"
        f"{formatted_history}"
        f"-------\n"
        f"Lembre-se: Responda diretamente à nova pergunta abaixo usando os dados acima se necessário."
    )
    
    new_input = "Qual é o meu codinome operacional mesmo? Confirme para mim."
    
    langchain_messages = [
        SystemMessage(content=enriched_system_prompt),
        HumanMessage(content=new_input)
    ]
    
    logger.info("Despachando payload com histórico estruturado para a IA...")
    
    response = await manager.invoke_with_fallback(langchain_messages)
    
    await brain.add_message(role="ai", content=response, session_id=session_id)
    
    print(f"\n\n[ATLAS INTEGRATED RESPONSE]: {response}\n")
    
    assert response is not None
    assert "Root-Alpha" in response, "A ATLAS ainda falhou em recuperar o codinome do histórico estruturado."
    
    logger.info("=== Teste de Integração de Memória Concluído com Sucesso ===")