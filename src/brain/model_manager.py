import datetime
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from src.tools import ATLAS_TOOLS
from config.settings import settings
from config.logger import logger

class AtlasModelManager:
    def __init__(self):
        logger.debug(f"Inicializando modelo local Ollama: {settings.OLLAMA_MODEL}")
        self.local_model = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=0.3,
            timeout=10.0  
        ).bind_tools(ATLAS_TOOLS)
        
        self.cloud_model = None
        if settings.GEMINI_API_KEY:
            logger.debug("Chave Gemini detectada. Inicializando modelo de contingência na nuvem.")
            self.cloud_model = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=settings.GEMINI_API_KEY,
                temperature=0.3
            ).bind_tools(ATLAS_TOOLS)
        else:
            logger.warning("GEMINI_API_KEY não foi configurada. Operando sem fallback.")

    async def invoke_with_fallback(self, payload: list) -> str:
        """
        Tenta processar a requisição no Ollama local com timeout rígido.
        Em caso de queda, indisponibilidade ou estouro, aciona o Gemini Flash.
        """
        payload = self._inject_temporal_context(payload)

        try:
            logger.debug("Direcionando requisição para o cérebro local (Ollama)...")
            response = await self.local_model.ainvoke(payload)
            return self._extract_content(response)
            
        except Exception as local_error:
            logger.warning(f"Ollama local indisponível ou rejeitou o payload: {local_error}")
            
            if self.cloud_model:
                logger.info("Protocolo de transbordo ativado. Acionando Gemini-1.5-Flash na nuvem...")
                try:
                    response = await self.cloud_model.ainvoke(payload)
                    return self._extract_content(response)
                except Exception as cloud_error:
                    logger.critical(f"Falha crítica: Ambos os motores de IA falharam. Erro nuvem: {cloud_error}")
                    return "Senhor, houve uma falha catastrófica em ambos os meus módulos de processamento centrais."
            else:
                logger.error("Falha no modelo local e nenhum modelo de nuvem configurado para fallback.")
                return "Senhor, meu módulo local está sobrecarregado e não possuo conexões de contingência acivas."

    def _inject_temporal_context(self, payload: list) -> list:
        """Injeta a data e hora atual do sistema operacional no prompt principal."""
        now = datetime.datetime.now()
        dias_semana = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
        data_formatada = f"{dias_semana[now.weekday()]}, {now.day} de {now.strftime('%B')} de {now.year}, às {now.strftime('%H:%M')}"
        
        for msg in payload:
            if isinstance(msg, SystemMessage):
                msg.content = f"DIRETRIZ TEMPORAL: Hoje é {data_formatada}.\n\n{msg.content}"
                break
        return payload

    def _extract_content(self, response) -> str:
        """Trata e extrai o conteúdo textual bruto de forma resiliente."""
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