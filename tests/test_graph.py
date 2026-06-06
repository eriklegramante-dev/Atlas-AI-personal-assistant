import pytest
from src.database.brain_database import AtlasBrain
from src.brain.agent_graph import AtlasBrainGraph
from config.logger import logger

@pytest.mark.asyncio
async def test_atlas_graph_execution():
    """
    Teste de integração para validar a execução do fluxo central via LangGraph.
    """
    logger.info("=== Iniciando Teste de Arquitetura LangGraph da ATLAS ===")
    
    brain = AtlasBrain()
    await brain.initialize_db()
    
    session_id = "test_graph_session"
    await brain.clear_session_history(session_id=session_id)
    
    await brain.add_message(role="human", content="Meu nome é Erik e sou o White Hat deste sistema.", session_id=session_id)
    await brain.add_message(role="ai", content="Registro efetuado, Operador Erik.", session_id=session_id)
    
    history = await brain.get_chat_history(session_id=session_id)
    
    graph = AtlasBrainGraph()
    
    user_query = "Quem sou eu e qual a minha diretriz de segurança registrada?"
    logger.info(f"Invocando o grafo com a pergunta: '{user_query}'")
    
    response = await graph.execute(
        user_input=user_query,
        history_raw=history,
        humor="40%"
    )
    
    assert response is not None
    assert "Erik" in response, "O grafo falhou em carregar e ler o estado de memória do banco."
    
    print(f"\n\n[LANGGRAPH RESPONSE]: {response}\n")
    logger.info("=== Teste de Execução de Estados Concluído com Sucesso ===")