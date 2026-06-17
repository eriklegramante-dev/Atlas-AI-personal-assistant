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
            """Nó que prepara o prompt estruturado e invoca a inteligência local ou nuvem."""
            logger.info("--- [DEBUG GRAPH] Nó _call_brain Iniciado ---")
            
            raw_history = state.get("chat_history_raw", [])
            user_input = state.get("input", "")
            humor = state.get("mood_humor", "30%")
            current_messages = state.get("messages", [])
            
            # 1. Reconstrói o bloco de System Prompt e a pergunta inicial de forma estática
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
            
            base_payload = [
                SystemMessage(content=enriched_system_prompt),
                HumanMessage(content=user_input)
            ]

            # 2. Montagem da linha do tempo para o modelo
            if not current_messages:
                payload = base_payload
            else:
                payload = base_payload + current_messages

            # 3. Invoca o gerenciador de IA (Ollama com fallback ativo)
            try:
                # Para manter o suporte a Tool Calls nativo dentro do LangGraph, 
                # nós precisamos invocar o modelo diretamente se ele possuir ferramentas acopladas.
                # O invoke_with_fallback devolve apenas texto bruto, o que quebra o reconhecimento de ferramentas do grafo.
                
                logger.debug("Invocando motor de IA dentro do fluxo do Grafo...")
                if self.model_manager.cloud_model:
                    # Se houver chave, usamos o modelo com fallback nativo do LangChain se preferir,
                    # ou chamamos o local_model diretamente para o grafo gerenciar as ferramentas
                    ai_message = await self.model_manager.local_model.ainvoke(payload)
                else:
                    ai_message = await self.model_manager.local_model.ainvoke(payload)
                    
                logger.info(f"[DEBUG GRAPH] Resposta do modelo gerada com sucesso. Conteúdo vazio? {not ai_message.content}")
                
                return {
                    "messages": [ai_message],
                    "response": ai_message.content if not ai_message.tool_calls else ""
                }
                
            except Exception as e:
                logger.warning(f"[DEBUG GRAPH] Instabilidade no modelo principal, tentando fallback: {e}")
                try:
                    if self.model_manager.cloud_model:
                        ai_message = await self.model_manager.cloud_model.ainvoke(payload)
                        return {"messages": [ai_message], "response": ai_message.content}
                except Exception as cloud_err:
                    logger.critical(f"[DEBUG GRAPH] Falha total nos motores de IA: {cloud_err}")
                    
                from langchain_core.messages import AIMessage
                error_msg = AIMessage(content="Senhor, enfrentei uma oscilação nos meus módulos de processamento central.")
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
            """Interface executável assíncrona para invocar o grafo por fora."""
            initial_state = {
                "input": user_input,
                "chat_history_raw": history_raw,
                "mood_humor": humor,
                "messages": []
            }
            
            # Executa o fluxo completo dos nós
            final_state = await self.app.ainvoke(initial_state)
            
            # 1. Tenta pegar a string direta do campo response
            response = final_state.get("response", "")
            
            # 2. Se o campo response veio vazio por conta do comportamento do nó, 
            # extraímos o texto diretamente da ÚLTIMA mensagem gerada pelo grafo
            if not response and final_state.get("messages"):
                last_msg = final_state["messages"][-1]
                response = getattr(last_msg, "content", "")
                
            logger.info(f"[DEBUG GRAPH] Resposta final extraída para o usuário: '{response[:50]}...'")
            return str(response).strip()