import pytest
from src.database.brain_database import AtlasBrain
from src.brain.agent_graph import AtlasBrainGraph
from config.logger import logger

@pytest.mark.asyncio
async def test_atlas_graph_tool_execution():
    """
    Teste de integração definitivo: Garante que o LangGraph intercepta a intenção
    do usuário, aciona o nó de ferramentas de hardware de forma autônoma e gera a resposta.
    """
    logger.info("=== Iniciando Teste de Automação de Ferramentas via LangGraph ===")
    
    brain = AtlasBrain()
    await brain.initialize_db()
    
    session_id = "test_graph_tools_session"
    await brain.clear_session_history(session_id=session_id)
    
    history = await brain.get_chat_history(session_id=session_id)
    graph = AtlasBrainGraph()
    
    user_query = "ATLAS, como estão os recursos de hardware do meu sistema operacional agora?"
    logger.info(f"Invocando o grafo com comando de hardware: '{user_query}'")
    
    response = await graph.execute(
        user_input=user_query,
        history_raw=history,
        humor="30%"
    )
    
    assert response is not None
    assert len(response.strip()) > 0
    assert any(keyword in response.lower() for keyword in ["cpu", "memória", "ram", "disponíveis", "gigabytes"]), \
        f"A resposta final da IA não parece conter o relatório de hardware esperado. Resposta: {response}"
    
    print(f"\n\n[LANGGRAPH TOOL AUTONOMOUS RESPONSE]: {response}\n")
    logger.info("=== Teste de Execução de Ferramenta no Grafo Concluído com Sucesso ===")