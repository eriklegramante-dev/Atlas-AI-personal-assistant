from typing import Annotated, TypedDict, List
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from src.brain.model_manager import AtlasModelManager
from src.tools import TOOLS_MAP  # Our dynamic tools map
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
        """Node that prepares the structured prompt and invokes local or cloud intelligence."""
        logger.info("--- [DEBUG GRAPH] Node _call_brain Started ---")
        
        raw_history = state.get("chat_history_raw", [])
        user_input = state.get("input", "")
        humor = state.get("mood_humor", "30%")
        current_messages = state.get("messages", [])
        
        formatted_history = ""
        for msg in raw_history:
            speaker = "User (Root)" if msg["role"] == "human" else "ATLAS (You)"
            formatted_history += f"[{speaker}]: {msg['content']}\n"
            
        base_system = settings.SYSTEM_PROMPT.format(mood_humor=humor)
        enriched_system_prompt = (
            f"{base_system}\n\n"
            f"CONTEXT OF PREVIOUS CONVERSATION (RECENT MEMORY):\n"
            f"-------\n{formatted_history}-------\n"
        )
        
        base_payload = [
            SystemMessage(content=enriched_system_prompt),
            HumanMessage(content=user_input)
        ]

        if not current_messages:
            payload = base_payload
        else:
            payload = base_payload + current_messages

        try:
            logger.debug("Invoking AI engine within Graph flow...")
            if self.model_manager.cloud_model:
                ai_message = await self.model_manager.local_model.ainvoke(payload)
            else:
                ai_message = await self.model_manager.local_model.ainvoke(payload)
                
            logger.info(f"[DEBUG GRAPH] Model response generated successfully. Empty content? {not ai_message.content}")

            if ai_message.content in ["diagnostico_sistema", "system_diagnostics"]:
                return {
                    "messages": [ai_message],
                    "response": ""
                }
            
            return {
                "messages": [ai_message],
                "response": ai_message.content if not ai_message.tool_calls else ""
            }
            
        except Exception as e:
            logger.warning(f"[DEBUG GRAPH] Instability in the main model, attempting a fallback: {e}")
            try:
                if self.model_manager.cloud_model:
                    ai_message = await self.model_manager.cloud_model.ainvoke(payload)
                    return {"messages": [ai_message], "response": ai_message.content}
            except Exception as cloud_err:
                logger.critical(f"[DEBUG GRAPH] Critical failure on both AI engines: {cloud_err}")
                
            from langchain_core.messages import AIMessage
            error_msg = AIMessage(content="Sir, I experienced a fluctuation in my central processing modules.")
            return {"messages": [error_msg], "response": error_msg.content}

    async def _execute_tools(self, state: AgentState) -> dict:
        """Node responsible for autonomously executing the tools requested by the AI."""
        logger.info("--- [DEBUG GRAPH] Starting node _execute_tools ---")
        last_message = state["messages"][-1]
        tool_messages = []

        logger.debug(f"[DEBUG GRAPH] Analyzing messages for execution. Last message contains tool_calls? {hasattr(last_message, 'tool_calls')}")
        if hasattr(last_message, "tool_calls"):
            logger.debug(f"[DEBUG GRAPH] Content of tool_calls: {last_message.tool_calls}")

        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]

            logger.info(f"[DEBUG GRAPH] Running real tool: '{tool_name}' with ID '{tool_id}' and arguments: {tool_args}")
            
            if tool_name in TOOLS_MAP:
                tool_result = await TOOLS_MAP[tool_name].ainvoke(input=tool_args)
                logger.info(f"[DEBUG GRAPH] Raw result returned by the Tool function: {tool_result}")
                
                t_msg = ToolMessage(content=str(tool_result), tool_call_id=tool_id)
                logger.debug(f"[DEBUG GRAPH] ToolMessage object successfully generated: {t_msg}")
                tool_messages.append(t_msg)
            else:
                logger.error(f"[DEBUG GRAPH] Error: Tool '{tool_name}' not found on the system map.")
                tool_messages.append(ToolMessage(content="Error: Tool not found.", tool_call_id=tool_id))

        logger.info(f"[DEBUG GRAPH] Node _execute_tools Completed. Returning {len(tool_messages)} ToolMessages to state.")
        return {"messages": tool_messages}

    def _router(self, state: AgentState) -> str:
        """Conditional edge that decides whether the graph routing moves to tool execution or terminates."""
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            logger.debug("Router identified 'tool_calls'. Diverting to tool execution node.")
            return "execute_tools"
        logger.debug("Router identified no external calls. Terminating execution cycle.")
        return "end"

    def _build_graph(self):
        """Maps and binds nodes and logical conditions into the workflow graph."""
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
        logger.info("Decision graph with tool support successfully compiled.")

    async def execute(self, user_input: str, history_raw: List[dict], humor: str = "30%") -> str:
        """Asynchronous executable interface to invoke the graph loop from external modules."""
        initial_state = {
            "input": user_input,
            "chat_history_raw": history_raw,
            "mood_humor": humor,
            "messages": []
        }
        
        final_state = await self.app.ainvoke(initial_state)
        response = final_state.get("response", "")
        
        if not response and final_state.get("messages"):
            last_msg = final_state["messages"][-1]
            response = getattr(last_msg, "content", "")
            
        logger.info(f"[DEBUG GRAPH] Final extracted response for user: '{response[:50]}...'")
        return str(response).strip()