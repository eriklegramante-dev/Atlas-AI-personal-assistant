import pytest
from src.database.brain_database import AtlasBrain
from src.brain.agent_graph import AtlasBrainGraph
from config.logger import logger

@pytest.mark.asyncio
async def test_atlas_graph_tool_execution():
    """
    Definitive integration test: Ensures LangGraph intercepts user intent,
    autonomously triggers the hardware tools node, and synthesizes the response.
    """
    logger.info("=== Starting Autonomous Tool Execution Test via LangGraph ===")
    
    brain = AtlasBrain()
    await brain.initialize_db()
    
    session_id = "test_graph_tools_session"
    await brain.clear_session_history(session_id=session_id)
    
    history = await brain.get_chat_history(session_id=session_id)
    graph = AtlasBrainGraph()
    
    user_query = "ATLAS, execute system diagnostics to check my current hardware telemetry."
    logger.info(f"Invoking graph engine with hardware instruction: '{user_query}'")
    
    response = await graph.execute(
        user_input=user_query,
        history_raw=history,
        humor="30%"
    )
    
    assert response is not None
    assert len(response.strip()) > 0
    assert any(keyword in response.lower() for keyword in ["cpu", "memory", "ram", "available", "gigabytes"]), \
        f"The final AI core response does not appear to contain the expected hardware metrics report. Response: {response}"
    
    print(f"\n\n[LANGGRAPH TOOL AUTONOMOUS RESPONSE]: {response}\n")
    logger.info("=== LangGraph Autonomous Tool Execution Node Test Completed Successfully ===")