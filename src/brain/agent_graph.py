from typing import Annotated, TypedDict, List
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from src.brain.model_manager import AtlasModelManager
from config.settings import settings
from config.logger import logger

class AgentState(TypedDict):
    """Estrutura que retém o estado de dados atual de um ciclo de decisão."""
    input: str                                    
    chat_history_raw: List[dict]                  
    mood_humor: str                                
    messages: Annotated[list, add_messages]        
    response: str                                  

class AtlasBrainGraph:
    def __init__(self):
        self.model_manager = AtlasModelManager()
        self.workflow = StateGraph(AgentState)
        self._build_graph()

    async def _call_brain(self, state: AgentState) -> dict:
        """Nó lógico que monta o contexto e invoca o cérebro (Ollama/Gemini)."""
        logger.debug("Nó [Call Brain] acionado no LangGraph.")
        
        raw_history = state.get("chat_history_raw", [])
        user_input = state.get("input", "")
        humor = state.get("mood_humor", "30%")
        
        formatted_history = ""
        for msg in raw_history:
            speaker = "Usuário (Root)" if msg["role"] == "human" else "ATLAS (Você)"
            formatted_history += f"[{speaker}]: {msg['content']}\n"
            
        base_system = settings.SYSTEM_PROMPT.format(mood_humor=humor)
        enriched_system_prompt = (
            f"{base_system}\n\n"
            f"CONTEXTO DE CONVERSA ANTERIOR (MEMÓRIA RECENTE):\n"
            f"-------\n{formatted_history}-------\n"
        )
        
        payload = [
            SystemMessage(content=enriched_system_prompt),
            HumanMessage(content=user_input)
        ]
        
        ai_response = await self.model_manager.invoke_with_fallback(payload)
        
        return {
            "messages": [ai_response],
            "response": ai_response
        }

    def _build_graph(self):
        """Mapeia a arquitetura, nós e conexões do grafo."""
        self.workflow.add_node("call_brain", self._call_brain)
        
        self.workflow.add_edge(START, "call_brain")
        self.workflow.add_edge("call_brain", END)
        
        self.app = self.workflow.compile()
        logger.info("Grafo de decisões LangGraph da ATLAS compilado com sucesso.")

    async def execute(self, user_input: str, history_raw: List[dict], humor: str = "30%") -> str:
        """Interface executável assíncrona para invocar o grafo por fora."""
        initial_state = {
            "input": user_input,
            "chat_history_raw": history_raw,
            "mood_humor": humor,
            "messages": []
        }
        
        final_state = await self.app.ainvoke(initial_state)
        return final_state.get("response", "Senhor, meu fluxo de processamento de estados falhou.")