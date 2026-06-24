import datetime
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from src.tools import ATLAS_TOOLS
from config.settings import settings
from config.logger import logger

class AtlasModelManager:
    def __init__(self):
        logger.debug(f"Initializing local Ollama model: {settings.OLLAMA_MODEL}")
        self.local_model = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=0.3,
            timeout=10.0  
        ).bind_tools(ATLAS_TOOLS)
        
        self.cloud_model = None
        if settings.GEMINI_API_KEY:
            logger.debug("Gemini API key detected. Initializing cloud contingency model.")
            self.cloud_model = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=settings.GEMINI_API_KEY,
                temperature=0.3
            ).bind_tools(ATLAS_TOOLS)
        else:
            logger.warning("GEMINI_API_KEY is not configured. Operating without fallback contingency.")

    async def invoke_with_fallback(self, payload: list) -> str:
            """
            Attempts to process the request on local Ollama with a strict timeout.
            If the model aggressively triggers a tool call intent instead of text,
            it automatically re-routes to a text-only instance to force a verbal response.
            """
            payload = self._inject_temporal_context(payload)

            try:
                logger.debug("Routing request to local brain engine (Ollama)...")
                response = await self.local_model.ainvoke(payload)
                extracted = self._extract_content(response)
                
                if "TOOL_CALL_INTENT" in extracted:
                    logger.warning("Local model generated an aggressive tool call intent during a text-only invocation. Forcing text mode rewrite...")
                    unbound_model = ChatOllama(
                        base_url=settings.OLLAMA_BASE_URL,
                        model=settings.OLLAMA_MODEL,
                        temperature=0.1, 
                        timeout=10.0
                    )
                    response = await unbound_model.ainvoke(payload)
                    return self._extract_content(response)
                    
                return extracted
                
            except Exception as local_error:
                logger.warning(f"Local Ollama unavailable or rejected the payload: {local_error}")
                
                if self.cloud_model:
                    logger.info("Overflow protocol activated. Invoking Gemini-2.5-Flash in the cloud...")
                    try:
                        response = await self.cloud_model.ainvoke(payload)
                        return self._extract_content(response)
                    except Exception as cloud_error:
                        logger.critical(f"Critical failure: Both AI engines failed. Cloud error: {cloud_error}")
                        return "Sir, I experienced a catastrophic failure across both central processing modules."
                else:
                    logger.error("Local model failure and no cloud model configured for fallback.")
                    return "Sir, my local module is overloaded and I possess no active contingency connections."

    def _inject_temporal_context(self, payload: list) -> list:
        """Injects current system date and time into the main SystemMessage prompt."""
        now = datetime.datetime.now()
        formatted_date = f"{now.strftime('%A')}, {now.day} of {now.strftime('%B')} of {now.year}, at {now.strftime('%H:%M')}"
        
        for msg in payload:
            if isinstance(msg, SystemMessage):
                msg.content = f"TEMPORAL DIRECTIVE: Today is {formatted_date}.\n\n{msg.content}"
                break
        return payload

    def _extract_content(self, response) -> str:
            """Resiliently processes and extracts raw text content or tool execution metadata from LLM responses."""
            if hasattr(response, "tool_calls") and response.tool_calls:
                tool_name = response.tool_calls[0].get("name", "unknown_tool")
                return f"TOOL_CALL_INTENT: {tool_name}"

            content = response.content
            if isinstance(content, list):
                extracted = []
                for item in content:
                    if isinstance(item, dict):
                        extracted.append(item.get("text", str(item)))
                    elif hasattr(item, "text"):
                        extracted.append(item.text)
                    else:
                        extracted.append(str(item))
                return "".join(extracted).strip()
            return str(content).strip()