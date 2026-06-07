from typing import Annotated, TypedDict, List
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from src.brain.model_manager import AtlasModelManager
from src.tools import TOOLS_MAP  # Nosso mapa de funções dinâmicas
from config.settings import settings
from config.logger import logger

class AgentState(TypedDict):
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
            """Nó que prepara o prompt estruturado e invoca a inteligência de forma resiliente."""
            logger.info("--- [DEBUG GRAPH] Iniciando nó _call_brain ---")
            
            raw_history = state.get("chat_history_raw", [])
            user_input = state.get("input", "")
            humor = state.get("mood_humor", "30%")
            current_messages = state.get("messages", [])
            
            logger.debug(f"[DEBUG GRAPH] Quantidade de mensagens acumuladas no estado atual: {len(current_messages)}")
            if current_messages:
                logger.debug(f"[DEBUG GRAPH] Tipo da última mensagem no estado: {type(current_messages[-1])}")
                logger.debug(f"[DEBUG GRAPH] Conteúdo da última mensagem: {getattr(current_messages[-1], 'content', 'Sem conteúdo')}")

            if not current_messages:
                logger.debug("[DEBUG GRAPH] Ciclo inicial detectado. Construindo System Prompt estruturado.")
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
            else:
                logger.debug("[DEBUG GRAPH] Ciclo de retorno de ferramenta detectado. Utilizando histórico de mensagens acumulado.")
                payload = current_messages

            logger.info(f"[DEBUG GRAPH] Enviando PAYLOAD contendo {len(payload)} mensagens para o Model Manager.")
            for i, msg in enumerate(payload):
                logger.debug(f" -> Mensagem [{i}] ({type(msg).__name__}): {str(msg.content)[:80]}...")
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    logger.debug(f"    └── Contém Tool Calls: {msg.tool_calls}")

            try:
                ai_response_text = await self.model_manager.invoke_with_fallback(payload)
                logger.info(f"[DEBUG GRAPH] Resposta textual recebida do Model Manager: '{ai_response_text[:60]}...'")
                
                if not current_messages and ("diagnostico_sistema" in user_input or "hardware" in user_input.lower()):
                    logger.debug("[DEBUG GRAPH] Interceptador de hardware ativado. Forçando injeção de ToolCall para estabilidade.")
                    from langchain_core.messages import AIMessage
                    import uuid
                    ai_message = AIMessage(
                        content="",
                        tool_calls=[{
                            "name": "diagnostico_sistema",
                            "args": {},
                            "id": f"call_{uuid.uuid4().hex[:8]}"
                        }]
                    )
                    logger.debug(f"[DEBUG GRAPH] Objeto AIMessage forçado gerado: {ai_message}")
                    return {"messages": [ai_message], "response": ""}
                    
                from langchain_core.messages import AIMessage
                ai_message = AIMessage(content=str(ai_response_text))
                return {
                    "messages": [ai_message],
                    "response": ai_message.content
                }
                
            except Exception as e:
                logger.error(f"[DEBUG GRAPH] Exceção capturada dentro do nó _call_brain: {e}", exc_info=True)
                from langchain_core.messages import AIMessage
                error_msg = AIMessage(content="Senhor, enfrentei uma instabilidade severa nos meus núcleos de processamento de estado.")
                return {"messages": [error_msg], "response": error_msg.content}

    async def _execute_tools(self, state: AgentState) -> dict:
        """Nó encarregado de executar de forma autônoma as ferramentas solicitadas pela IA."""
        logger.info("--- [DEBUG GRAPH] Iniciando nó _execute_tools ---")
        last_message = state["messages"][-1]
        tool_messages = []

        logger.debug(f"[DEBUG GRAPH] Analisando mensagens para execução. Última mensagem possui tool_calls? {hasattr(last_message, 'tool_calls')}")
        if hasattr(last_message, "tool_calls"):
            logger.debug(f"[DEBUG GRAPH] Conteúdo de tool_calls: {last_message.tool_calls}")

        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]

            logger.info(f"[DEBUG GRAPH] Executando ferramenta real: '{tool_name}' com ID '{tool_id}'")
            
            if tool_name in TOOLS_MAP:
                tool_result = await TOOLS_MAP[tool_name].ainvoke(input=tool_args)
                logger.info(f"[DEBUG GRAPH] Resultado bruto retornado pela função da Tool: {tool_result}")
                
                t_msg = ToolMessage(content=str(tool_result), tool_call_id=tool_id)
                logger.debug(f"[DEBUG GRAPH] Objeto ToolMessage gerado com sucesso: {t_msg}")
                tool_messages.append(t_msg)
            else:
                logger.error(f"[DEBUG GRAPH] Erro: Ferramenta '{tool_name}' não encontrada no mapa do sistema.")
                tool_messages.append(ToolMessage(content="Erro: Ferramenta não encontrada.", tool_call_id=tool_id))

        logger.info(f"[DEBUG GRAPH] Nó _execute_tools concluído. Devolvendo {len(tool_messages)} ToolMessages para o estado.")
        return {"messages": tool_messages}

    async def _execute_tools(self, state: AgentState) -> dict:
        """Nó encarregado de executar de forma autônoma as ferramentas solicitadas pela IA."""
        logger.info("Nó [Execute Tools] acionado.")
        last_message = state["messages"][-1]
        tool_messages = []

        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]

            logger.info(f"Executando ferramenta interna: {tool_name} com argumentos: {tool_args}")
            
            if tool_name in TOOLS_MAP:
                tool_result = await TOOLS_MAP[tool_name].ainvoke(input=tool_args)
                
                tool_messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_id))
            else:
                logger.error(f"A ferramenta solicitada '{tool_name}' não está mapeada no sistema.")
                tool_messages.append(ToolMessage(content="Erro: Ferramenta não encontrada.", tool_call_id=tool_id))

        return {"messages": tool_messages}

    def _router(self, state: AgentState) -> str:
        """Aresta condicional que decide se o grafo vai para a execução de ferramentas ou encerra."""
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            logger.debug("Roteador identificou 'tool_calls'. Desviando para execução de ferramentas.")
            return "execute_tools"
        logger.debug("Roteador não identificou chamadas externas. Encerrando ciclo.")
        return "end"

    def _build_graph(self):
        """Mapeia e amarra os nós e as condições lógicas do fluxo."""
        self.workflow.add_node("call_brain", self._call_brain)
        self.workflow.add_node("execute_tools", self._execute_tools)
        
        self.workflow.add_edge(START, "call_brain")
        
        self.workflow.add_conditional_edges(
            "call_brain",
            self._router,
            {
                "execute_tools": "execute_tools",
                "end": END
            }
        )
        
        self.workflow.add_edge("execute_tools", "call_brain")
        
        self.app = self.workflow.compile()
        logger.info("Grafo de decisões com suporte a ferramentas compilado com sucesso.")

    async def execute(self, user_input: str, history_raw: List[dict], humor: str = "30%") -> str:
        initial_state = {
            "input": user_input,
            "chat_history_raw": history_raw,
            "mood_humor": humor,
            "messages": []
        }
        final_state = await self.app.ainvoke(initial_state)
        return final_state.get("response", "Senhor, meu fluxo de processamento de estados falhou.")